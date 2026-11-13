from ninja import Router
from ninja.pagination import paginate

from ..models import Budget
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import BudgetIn, BudgetOut, BudgetUpdate

router = Router(tags=["Budgets"])


def _budgets(user):
    return Budget.objects.filter(team_id__in=team_ids_for(user))


@router.get("/", response=list[BudgetOut])
@paginate
def list_budgets(request, team_id: int | None = None):
    qs = _budgets(request.auth)
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@router.post("/", response={201: BudgetOut})
def create_budget(request, payload: BudgetIn):
    require_team_member(request.auth, payload.team_id)
    return 201, Budget.objects.create(**payload.model_dump(), created_by=request.auth)


@router.get("/{id}", response=BudgetOut)
def get_budget(request, id: int):
    return get_or_404(_budgets(request.auth), id)


@router.patch("/{id}", response=BudgetOut)
def update_budget(request, id: int, payload: BudgetUpdate):
    budget = get_or_404(_budgets(request.auth), id)
    return apply_patch(budget, payload)


@router.delete("/{id}", response={204: None})
def delete_budget(request, id: int):
    budget = get_or_404(_budgets(request.auth), id)
    budget.delete()
    return 204, None
