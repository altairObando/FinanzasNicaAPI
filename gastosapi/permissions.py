from ninja.errors import HttpError

from .models import Team, TeamMember


def team_ids_for(user):
    return TeamMember.objects.filter(member=user).values_list("team_id", flat=True)


def require_team_member(user, team_id: int) -> Team:
    team = Team.objects.filter(pk=team_id, team_members__member=user).first()
    if not team:
        raise HttpError(404, "Equipo no encontrado")
    return team


def require_team_owner(user, team_id: int) -> Team:
    team = require_team_member(user, team_id)
    if not TeamMember.objects.filter(team=team, member=user, is_team_owner=True).exists():
        raise HttpError(403, "Solo el dueño del equipo puede hacer esto")
    return team


def get_or_404(qs, pk: int, message="No encontrado"):
    obj = qs.filter(pk=pk).first()
    if not obj:
        raise HttpError(404, message)
    return obj


def apply_patch(instance, payload):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()
    return instance


def refresh_member_count(team: Team):
    team.members = team.team_members.count()
    team.save(update_fields=["members"])
