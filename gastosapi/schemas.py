from datetime import date as Date
from datetime import datetime as DateTime
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import (
    Account,
    AccountMovement,
    Budget,
    Category,
    Credit,
    CreditInstallment,
    Expense,
    ExpenseInvoice,
    Team,
    TeamMember,
)


class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    token: str


class UserOut(Schema):
    id: int
    username: str
    email: str


class TeamIn(Schema):
    name: str
    description: str | None = None


class TeamUpdate(Schema):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TeamOut(ModelSchema):
    class Meta:
        model = Team
        fields = "__all__"


class TeamMemberIn(Schema):
    team_id: int
    member_id: int
    account_limit: Decimal = Decimal("0.00")
    is_team_owner: bool = False


class TeamMemberUpdate(Schema):
    account_limit: Decimal | None = None
    is_team_owner: bool | None = None


class TeamMemberOut(ModelSchema):
    class Meta:
        model = TeamMember
        fields = "__all__"


class CategoryIn(Schema):
    team_id: int
    name: str
    description: str | None = None
    type: str = "OUT"
    icon: str
    color: str
    is_active: bool = True


class CategoryUpdate(Schema):
    name: str | None = None
    description: str | None = None
    type: str | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class CategoryOut(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"


class AccountIn(Schema):
    team_id: int
    name: str
    description: str | None = None
    currency: str = "NIO"
    opening_price: Decimal = Decimal("0.00")
    limit_per_day: Decimal = Decimal("0.00")
    icon: str
    color: str
    is_active: bool = True


class AccountUpdate(Schema):
    name: str | None = None
    description: str | None = None
    currency: str | None = None
    opening_price: Decimal | None = None
    limit_per_day: Decimal | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class AccountOut(ModelSchema):
    balance: Decimal

    class Meta:
        model = Account
        fields = "__all__"

    @staticmethod
    def resolve_balance(obj):
        return obj.balance()


class AccountMovementIn(Schema):
    account_id: int
    amount: Decimal
    reference: str | None = None
    tx_date: DateTime
    mov_type: str = "TX"


class AccountMovementUpdate(Schema):
    amount: Decimal | None = None
    reference: str | None = None
    tx_date: DateTime | None = None
    mov_type: str | None = None


class AccountMovementOut(ModelSchema):
    class Meta:
        model = AccountMovement
        fields = "__all__"


class BudgetIn(Schema):
    team_id: int
    name: str
    description: str | None = None
    limit: Decimal = Decimal("0.00")
    start_date: Date
    end_date: Date
    icon: str
    color: str
    is_active: bool = True


class BudgetUpdate(Schema):
    name: str | None = None
    description: str | None = None
    limit: Decimal | None = None
    start_date: Date | None = None
    end_date: Date | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class BudgetOut(ModelSchema):
    class Meta:
        model = Budget
        fields = "__all__"


class CreditIn(Schema):
    team_id: int
    name: str
    description: str | None = None
    amount: Decimal = Decimal("0.00")
    no_installments: int
    periodicity: str | None = None
    duration: int = 1
    first_installment: Date
    icon: str
    color: str
    is_active: bool = True


class CreditUpdate(Schema):
    name: str | None = None
    description: str | None = None
    amount: Decimal | None = None
    no_installments: int | None = None
    periodicity: str | None = None
    duration: int | None = None
    first_installment: Date | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class CreditOut(ModelSchema):
    is_paid: bool

    class Meta:
        model = Credit
        fields = "__all__"

    @staticmethod
    def resolve_is_paid(obj):
        return obj.is_paid()


class CreditInstallmentIn(Schema):
    credit_id: int
    description: str | None = None
    number_in_year: int
    contract_year: int
    due_amout: Decimal
    due_date: Date
    payed: Decimal = Decimal("0.00")
    payed_date: Date


class CreditInstallmentUpdate(Schema):
    description: str | None = None
    number_in_year: int | None = None
    contract_year: int | None = None
    due_amout: Decimal | None = None
    due_date: Date | None = None
    payed: Decimal | None = None
    payed_date: Date | None = None


class CreditInstallmentOut(ModelSchema):
    class Meta:
        model = CreditInstallment
        fields = "__all__"


class ExpenseIn(Schema):
    team_id: int
    account_id: int
    category_id: int
    budget_id: int | None = None
    credit_id: int | None = None
    amount: Decimal
    reference: str
    description: str | None = None
    date: Date
    tags: str | None = None


class ExpenseUpdate(Schema):
    account_id: int | None = None
    category_id: int | None = None
    budget_id: int | None = None
    credit_id: int | None = None
    amount: Decimal | None = None
    reference: str | None = None
    description: str | None = None
    date: Date | None = None
    tags: str | None = None


class ExpenseOut(ModelSchema):
    class Meta:
        model = Expense
        fields = "__all__"


class ExpenseInvoiceOut(ModelSchema):
    class Meta:
        model = ExpenseInvoice
        fields = "__all__"
