from ninja import Router
from ninja.pagination import paginate

from ..models import Credit, CreditInstallment
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import (
    CreditIn,
    CreditInstallmentIn,
    CreditInstallmentOut,
    CreditInstallmentUpdate,
    CreditOut,
    CreditUpdate,
)

router = Router(tags=["Credits"])
installments_router = Router(tags=["Credit installments"])


def _credits(user):
    return Credit.objects.filter(team_id__in=team_ids_for(user))


def _installments(user):
    return CreditInstallment.objects.filter(credit__team_id__in=team_ids_for(user))


@router.get("/", response=list[CreditOut])
@paginate
def list_credits(request, team_id: int | None = None):
    qs = _credits(request.auth)
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@router.post("/", response={201: CreditOut})
def create_credit(request, payload: CreditIn):
    require_team_member(request.auth, payload.team_id)
    return 201, Credit.objects.create(**payload.model_dump(), created_by=request.auth)


@router.get("/{id}", response=CreditOut)
def get_credit(request, id: int):
    return get_or_404(_credits(request.auth), id)


@router.patch("/{id}", response=CreditOut)
def update_credit(request, id: int, payload: CreditUpdate):
    credit = get_or_404(_credits(request.auth), id)
    return apply_patch(credit, payload)


@router.delete("/{id}", response={204: None})
def delete_credit(request, id: int):
    credit = get_or_404(_credits(request.auth), id)
    credit.delete()
    return 204, None


@installments_router.get("/", response=list[CreditInstallmentOut])
@paginate
def list_installments(request, credit_id: int | None = None):
    qs = _installments(request.auth)
    if credit_id is not None:
        get_or_404(_credits(request.auth), credit_id)
        qs = qs.filter(credit_id=credit_id)
    return qs


@installments_router.post("/", response={201: CreditInstallmentOut})
def create_installment(request, payload: CreditInstallmentIn):
    get_or_404(_credits(request.auth), payload.credit_id)
    return 201, CreditInstallment.objects.create(**payload.model_dump())


@installments_router.get("/{id}", response=CreditInstallmentOut)
def get_installment(request, id: int):
    return get_or_404(_installments(request.auth), id)


@installments_router.patch("/{id}", response=CreditInstallmentOut)
def update_installment(request, id: int, payload: CreditInstallmentUpdate):
    installment = get_or_404(_installments(request.auth), id)
    return apply_patch(installment, payload)


@installments_router.delete("/{id}", response={204: None})
def delete_installment(request, id: int):
    installment = get_or_404(_installments(request.auth), id)
    installment.delete()
    return 204, None
