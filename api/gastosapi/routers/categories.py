from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from ..models import Category, CategoryType
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for, get_team_id_for
from ..schemas import CategoryIn, CategoryOut, CategoryUpdate, CategorySummary

router = Router(tags=["Categories"])

CATEGORY_TYPES = {choice.value for choice in CategoryType}


@router.get("/", response=list[CategoryOut])
@paginate
def list_categories(
    request,
    team_id: int | None = None,
    name: str | None = None,
    type: str | None = None,
):
    qs = Category.objects.filter(team_id__in=team_ids_for(request.auth))
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    if name is not None:
        qs = qs.filter(name__icontains=name)
    if type is not None:
        if type not in CATEGORY_TYPES:
            raise HttpError(400, "Tipo de categoría inválido")
        qs = qs.filter(type=type)
    return qs

@router.get('/summary',response=CategorySummary)
def get_summary(request, team_code: str | None = None):
    result = {"total":0,"income": 0, "expense": 0, "items": [] }
    qs = Category.objects.filter(team_id__in=team_ids_for(request.auth),is_active=True)
    if team_code is not None:
        qs = qs.filter(team_id=get_team_id_for(request.auth, team_code))
    result['total'] = qs.count()
    result['income'] = qs.filter(type=CategoryType.INCOME).count()
    result['expense'] = qs.filter(type=CategoryType.EXPENSE).count()
    result['items'] = qs[:4]

    return CategorySummary( total=result['total'], expense=result['expense'], income=result['income'], items=result['items']  )




@router.post("/", response={201: CategoryOut})
def create_category(request, payload: CategoryIn):
    require_team_member(request.auth, payload.team_id)
    return 201, Category.objects.create(**payload.model_dump(), created_by=request.auth)


@router.post("/bulk", response={201: list[CategoryOut]})
def bulk_create_categories(request, payload: list[CategoryIn]):
    if not payload:
        raise HttpError(400, "La lista de categorías no puede estar vacía")

    invalid_types = [item.type for item in payload if item.type not in CATEGORY_TYPES]
    if invalid_types:
        raise HttpError(400, f"Tipo de categoría inválido: {invalid_types[0]}")

    for team_id in {item.team_id for item in payload}:
        require_team_member(request.auth, team_id)

    with transaction.atomic():
        categories = Category.objects.bulk_create(
            [Category(**item.model_dump(), created_by=request.auth) for item in payload]
        )
    return 201, categories


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
