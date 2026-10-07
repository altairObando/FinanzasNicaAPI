from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from ..models import Team, TeamMember
from ..permissions import (
    apply_patch,
    get_or_404,
    refresh_member_count,
    require_team_member,
    require_team_owner,
    team_ids_for,
)
from ..schemas import (
    TeamIn,
    TeamMemberIn,
    TeamMemberOut,
    TeamMemberUpdate,
    TeamOut,
    TeamUpdate,
)

router = Router(tags=["Teams"])
members_router = Router(tags=["Team members"])


@router.get("/", response=list[TeamOut])
@paginate
def list_teams(request):
    return Team.objects.filter(pk__in=team_ids_for(request.auth)).distinct()


@router.post("/", response={201: TeamOut})
def create_team(request, payload: TeamIn):
    team = Team.objects.create(**payload.model_dump())
    TeamMember.objects.create(
        team=team,
        member=request.auth,
        created_by=request.auth,
        is_team_owner=True,
    )
    refresh_member_count(team)
    return 201, team


@router.get("/{id}", response=TeamOut)
def get_team(request, id: int):
    return require_team_member(request.auth, id)


@router.patch("/{id}", response=TeamOut)
def update_team(request, id: int, payload: TeamUpdate):
    team = require_team_owner(request.auth, id)
    return apply_patch(team, payload)


@router.delete("/{id}", response={204: None})
def delete_team(request, id: int):
    team = require_team_owner(request.auth, id)
    team.delete()
    return 204, None


@members_router.get("/", response=list[TeamMemberOut])
@paginate
def list_members(request, team_id: int | None = None):
    qs = TeamMember.objects.filter(team_id__in=team_ids_for(request.auth)).select_related(
        "team", "member", "created_by"
    )
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@members_router.post("/", response={201: TeamMemberOut})
def create_member(request, payload: TeamMemberIn):
    require_team_member(request.auth, payload.team_id)
    if TeamMember.objects.filter(team_id=payload.team_id, member_id=payload.member_id).exists():
        raise HttpError(400, "El usuario ya es miembro de este equipo")
    member = TeamMember.objects.create(**payload.model_dump(), created_by=request.auth)
    refresh_member_count(member.team)
    return 201, member


@members_router.get("/{id}", response=TeamMemberOut)
def get_member(request, id: int):
    return get_or_404(TeamMember.objects.filter(team_id__in=team_ids_for(request.auth)), id)


@members_router.patch("/{id}", response=TeamMemberOut)
def update_member(request, id: int, payload: TeamMemberUpdate):
    member = get_or_404(TeamMember.objects.filter(team_id__in=team_ids_for(request.auth)), id)
    require_team_owner(request.auth, member.team_id)
    return apply_patch(member, payload)


@members_router.delete("/{id}", response={204: None})
def delete_member(request, id: int):
    member = get_or_404(TeamMember.objects.filter(team_id__in=team_ids_for(request.auth)), id)
    require_team_owner(request.auth, member.team_id)
    if member.is_team_owner:
        owners = TeamMember.objects.filter(team=member.team, is_team_owner=True).count()
        if owners <= 1:
            raise HttpError(400, "No se puede eliminar al único dueño")
    team = member.team
    member.delete()
    refresh_member_count(team)
    return 204, None
