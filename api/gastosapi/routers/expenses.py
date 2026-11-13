from ninja import File, Router, UploadedFile
from ninja.pagination import paginate

from ..models import Account, Budget, Category, CreditInstallment, Expense, ExpenseInvoice
from ..permissions import apply_patch, get_or_404, require_team_member, team_ids_for
from ..schemas import ExpenseIn, ExpenseInvoiceOut, ExpenseOut, ExpenseUpdate

router = Router(tags=["Expenses"])
invoices_router = Router(tags=["Expense invoices"])


def _expenses(user):
    return Expense.objects.filter(team_id__in=team_ids_for(user))


def _invoices(user):
    return ExpenseInvoice.objects.filter(expense__team_id__in=team_ids_for(user))


def _validate_expense_fks(user, team_id, account_id, category_id, budget_id, credit_id):
    require_team_member(user, team_id)
    ids = team_ids_for(user)
    get_or_404(Account.objects.filter(team_id__in=ids), account_id, "Cuenta no encontrada")
    get_or_404(Category.objects.filter(team_id__in=ids), category_id, "Categoría no encontrada")
    if budget_id is not None:
        get_or_404(Budget.objects.filter(team_id__in=ids), budget_id, "Presupuesto no encontrado")
    if credit_id is not None:
        get_or_404(
            CreditInstallment.objects.filter(credit__team_id__in=ids),
            credit_id,
            "Cuota no encontrada",
        )


@router.get("/", response=list[ExpenseOut])
@paginate
def list_expenses(request, team_id: int | None = None):
    qs = _expenses(request.auth)
    if team_id is not None:
        require_team_member(request.auth, team_id)
        qs = qs.filter(team_id=team_id)
    return qs


@router.post("/", response={201: ExpenseOut})
def create_expense(request, payload: ExpenseIn):
    _validate_expense_fks(
        request.auth,
        payload.team_id,
        payload.account_id,
        payload.category_id,
        payload.budget_id,
        payload.credit_id,
    )
    return 201, Expense.objects.create(**payload.model_dump(), created_by=request.auth)


@router.get("/{id}", response=ExpenseOut)
def get_expense(request, id: int):
    return get_or_404(_expenses(request.auth), id)


@router.patch("/{id}", response=ExpenseOut)
def update_expense(request, id: int, payload: ExpenseUpdate):
    expense = get_or_404(_expenses(request.auth), id)
    data = payload.model_dump(exclude_unset=True)
    _validate_expense_fks(
        request.auth,
        expense.team_id,
        data.get("account_id", expense.account_id),
        data.get("category_id", expense.category_id),
        data.get("budget_id", expense.budget_id) if "budget_id" in data else expense.budget_id,
        data.get("credit_id", expense.credit_id) if "credit_id" in data else expense.credit_id,
    )
    return apply_patch(expense, payload)


@router.delete("/{id}", response={204: None})
def delete_expense(request, id: int):
    expense = get_or_404(_expenses(request.auth), id)
    expense.delete()
    return 204, None


@invoices_router.get("/", response=list[ExpenseInvoiceOut])
@paginate
def list_invoices(request, expense_id: int | None = None):
    qs = _invoices(request.auth)
    if expense_id is not None:
        get_or_404(_expenses(request.auth), expense_id)
        qs = qs.filter(expense_id=expense_id)
    return qs


@invoices_router.post("/", response={201: ExpenseInvoiceOut})
def create_invoice(request, expense_id: int, file: UploadedFile = File(...)):
    expense = get_or_404(_expenses(request.auth), expense_id)
    invoice = ExpenseInvoice.objects.create(
        expense=expense,
        created_by=request.auth,
        file=file,
    )
    return 201, invoice


@invoices_router.get("/{id}", response=ExpenseInvoiceOut)
def get_invoice(request, id: int):
    return get_or_404(_invoices(request.auth), id)


@invoices_router.delete("/{id}", response={204: None})
def delete_invoice(request, id: int):
    invoice = get_or_404(_invoices(request.auth), id)
    invoice.delete()
    return 204, None
