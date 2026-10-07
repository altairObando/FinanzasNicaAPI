from ninja import Router
from ninja.pagination import paginate

from ..models import Category
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import CategoryIn, CategoryOut, CategoryUpdate

router = Router(tags=["Categories"])


@router.get("/", response=list[CategoryOut])
@paginate
def list_categories(request, team_id: int | None = None):
    qs = Category.objects.filter(team_id__in=team_ids_for(request.auth))
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@router.post("/", response={201: CategoryOut})
def create_category(request, payload: CategoryIn):
    require_team_member(request.auth, payload.team_id)
    return 201, Category.objects.create(**payload.model_dump(), created_by=request.auth)


@router.get("/{id}", response=CategoryOut)
def get_category(request, id: int):
    return get_or_404(Category.objects.filter(team_id__in=team_ids_for(request.auth)), id)


@router.patch("/{id}", response=CategoryOut)
def update_category(request, id: int, payload: CategoryUpdate):
    category = get_or_404(Category.objects.filter(team_id__in=team_ids_for(request.auth)), id)
    return apply_patch(category, payload)


@router.delete("/{id}", response={204: None})
def delete_category(request, id: int):
    category = get_or_404(Category.objects.filter(team_id__in=team_ids_for(request.auth)), id)
    category.delete()
    return 204, None
