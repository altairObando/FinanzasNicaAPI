import logging

import requests
from ninja import Router
from ninja.pagination import paginate
from ninja.errors import HttpError
from django.utils import timezone
from django.db import DatabaseError, transaction
from django.db.models import Sum
from ..models import Account, AccountMovement, MovementType
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import (
    AccountIn,
    AccountMovementIn,
    AccountMovementOut,
    AccountMovementUpdate,
    AccountOut,
    AccountUpdate,
    AccountSummary,
    ExchangeRate,
)

router = Router(tags=["Accounts"])
movements_router = Router(tags=["Account movements"])
logger = logging.getLogger(__name__)


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

@router.get('/summary', response=list[AccountSummary])
def account_summary(request, team_id: int | None = None):
    qs = _accounts(request.auth)
    if team_id is not None:
        qs = qs.filter(team_id=team_id)
    summary = qs.annotate(total=Sum('movements__amount', default=0))

    return summary


@router.get('/exchange_rate', response=list[ExchangeRate])
def exchange_rate(request):
    try:
        url = 'https://api.frankfurter.dev/v2/rates?base=nio'
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
        rates = response.json()
        allowed_rates = ['USD', 'EUR', 'TWD', 'TND']
        result = list(filter(lambda rate: rate.get('quote') in allowed_rates, rates))
        return result
    except requests.exceptions.HTTPError as err:
        raise HttpError(err.response.status_code, "El servicio rechazó la petición")
    except requests.exceptions.RequestException:
        raise HttpError(503, "Error de comunicación con el servicio externo")

@router.post("/", response={201: AccountOut})
def create_account(request, payload: AccountIn):
    require_team_member(request.auth, payload.team_id)
    try:
        with transaction.atomic():
            new_account = Account.objects.create(
                **payload.model_dump(),
                created_by=request.auth,
            )
            if new_account.opening_price != 0:
                AccountMovement.objects.create(
                    account=new_account,
                    amount=new_account.opening_price,
                    reference="Opening Balance",
                    tx_date=timezone.now(),
                    mov_type=MovementType.TX,
                    created_by=request.auth,
                )
    except DatabaseError:
        logger.exception(
            "No se pudo crear la cuenta %s para el usuario %s",
            payload.name,
            request.auth.pk,
        )
        raise HttpError(500, "No se pudo crear la cuenta")

    return 201, new_account


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
