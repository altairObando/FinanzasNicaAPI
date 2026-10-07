from ninja import Router
from ninja.pagination import paginate

from ..models import Account, AccountMovement
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import (
    AccountIn,
    AccountMovementIn,
    AccountMovementOut,
    AccountMovementUpdate,
    AccountOut,
    AccountUpdate,
)

router = Router(tags=["Accounts"])
movements_router = Router(tags=["Account movements"])


def _accounts(user):
    return Account.objects.filter(team_id__in=team_ids_for(user))


def _movements(user):
    return AccountMovement.objects.filter(account__team_id__in=team_ids_for(user))


@router.get("/", response=list[AccountOut])
@paginate
def list_accounts(request, team_id: int | None = None):
    qs = _accounts(request.auth)
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@router.post("/", response={201: AccountOut})
def create_account(request, payload: AccountIn):
    require_team_member(request.auth, payload.team_id)
    return 201, Account.objects.create(**payload.model_dump(), created_by=request.auth)


@router.get("/{id}", response=AccountOut)
def get_account(request, id: int):
    return get_or_404(_accounts(request.auth), id)


@router.patch("/{id}", response=AccountOut)
def update_account(request, id: int, payload: AccountUpdate):
    account = get_or_404(_accounts(request.auth), id)
    return apply_patch(account, payload)


@router.delete("/{id}", response={204: None})
def delete_account(request, id: int):
    account = get_or_404(_accounts(request.auth), id)
    account.delete()
    return 204, None


@movements_router.get("/", response=list[AccountMovementOut])
@paginate
def list_movements(request, account_id: int | None = None):
    qs = _movements(request.auth)
    if account_id is not None:
        get_or_404(_accounts(request.auth), account_id)
        qs = qs.filter(account_id=account_id)
    return qs


@movements_router.post("/", response={201: AccountMovementOut})
def create_movement(request, payload: AccountMovementIn):
    get_or_404(_accounts(request.auth), payload.account_id)
    return 201, AccountMovement.objects.create(**payload.model_dump(), created_by=request.auth)


@movements_router.get("/{id}", response=AccountMovementOut)
def get_movement(request, id: int):
    return get_or_404(_movements(request.auth), id)


@movements_router.patch("/{id}", response=AccountMovementOut)
def update_movement(request, id: int, payload: AccountMovementUpdate):
    movement = get_or_404(_movements(request.auth), id)
    return apply_patch(movement, payload)


@movements_router.delete("/{id}", response={204: None})
def delete_movement(request, id: int):
    movement = get_or_404(_movements(request.auth), id)
    movement.delete()
    return 204, None
