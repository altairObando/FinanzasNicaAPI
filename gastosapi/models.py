import secrets
from finanzasnica.util import generate_code
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

# Create your models here.
class BaseModelIsActive(models.Model):
    is_active = models.BooleanField(default=True)
    class Meta:
        abstract = True

class BaseModelTime(models.Model):
    created_at = models.DateTimeField( auto_now_add=True )
    updated_at = models.DateTimeField( auto_now=True )
    class Meta:
        abstract = True

class BaseVisualItem(models.Model):
    icon = models.CharField( max_length=25 ) # MaterialCommunity Icons
    color= models.CharField( max_length=25 ) # hex/rgba
    class Meta:
        abstract = True

class BaseCreatedBy(models.Model):
    created_by = models.ForeignKey( 
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_related'
    )
    class Meta:
        abstract = True

class Currencies(models.TextChoices):
    NIO = "NIO", _("Córdoba Oro")
    USD = "USD", _("United States Dollar")
    EUR = "EUR", _("Euro")

class MovementType(models.TextChoices):
    TX = "TX", _("Transfer")
    EX = "EX", _("Expense")
    PY = "PY", _("Payment")

class Periodicity(models.TextChoices):
    Y = "Y", _("Yearly")
    S = "S", _("Half-yearly")
    Q = "Q", _("Quarterly")
    M = "M", _("Monthly")
    D = "D", _("Daily")
    
class Team(BaseModelTime, BaseModelIsActive):
    code = models.CharField( max_length=10, unique=True, editable=False )
    name = models.CharField( max_length=100 )
    description = models.TextField( blank=True, null=True )
    members = models.IntegerField(default=0, null=True)
    def __str__(self):
        return self.name

    def save(self, *args , **kwargs):
        if not self.code:
            self.code = generate_code()
            while Team.objects.filter(code=self.code).exists():
                self.code = generate_code()
        super().save(*args, **kwargs)

# BaseCreatedBy example userinstancename.TeamMembers_related
class TeamMember(BaseModelTime, BaseCreatedBy):
    team   = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teams')
    account_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_team_owner = models.BooleanField( default=False)

class CategoryType(models.TextChoices):
    INCOME = "IN", _("Ingreso (Suma)")
    EXPENSE = "OUT", _("Gasto (Resta)")

class Category(BaseModelTime, BaseModelIsActive, BaseVisualItem, BaseCreatedBy):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField( max_length=100 )
    description = models.TextField( blank=True, null=True )
    type = models.CharField(
        max_length=3, 
        choices=CategoryType.choices, 
        default=CategoryType.EXPENSE
    )

# BaseCreatedBy example userinstancename.Accounts_related
class Account(BaseModelTime, BaseModelIsActive, BaseVisualItem, BaseCreatedBy):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=Currencies, default=Currencies.NIO)
    opening_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    limit_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def balance(self):
        result = self.movements.aggregate(total=Sum('amount'))
        return result['total'] or 0

class AccountMovement(BaseCreatedBy):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='movements')
    amount = models.DecimalField(max_digits=12, decimal_places=2 )
    reference = models.CharField(max_length=150, blank=True, null=True)
    tx_date = models.DateTimeField('Transaction date')
    mov_type = models.CharField(max_length=2, choices=MovementType, default=MovementType.TX)

class Budget(BaseModelTime, BaseModelIsActive, BaseVisualItem, BaseCreatedBy):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    start_date = models.DateField()
    end_date = models.DateField()

class Credit(BaseModelTime, BaseModelIsActive, BaseVisualItem, BaseCreatedBy):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='credits')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    no_installments = models.IntegerField()
    periodicity = models.CharField(max_length=1, choices=Periodicity, default=None, null=True)
    duration = models.IntegerField(default=1)
    first_installment = models.DateField()

    def is_paid(self):
        result = self.installments.aggregate(total=Sum('payed'))
        return self.amount <= (result['total'] or 0)

class CreditInstallment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='installments')
    description = models.TextField(blank=True, null=True)
    number_in_year = models.IntegerField()
    contract_year = models.IntegerField()
    due_amout = models.DecimalField( max_digits=12, decimal_places=2 )
    due_date  = models.DateField()
    payed = models.DecimalField( max_digits=12, decimal_places=2 )
    payed_date = models.DateField()

class Expense( BaseModelTime, BaseCreatedBy ):
    team     = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='expenses')
    account  = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses')
    # registrar gasto reflejado en presupuestos
    budget   = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses', null=True)
    # registrar gasto reflejado como pago de una cuota.
    credit     = models.ForeignKey(CreditInstallment, on_delete=models.CASCADE, related_name='expenses', null=True)
    amount     = models.DecimalField( max_digits=12, decimal_places=2 )
    reference = models.CharField( max_length = 150)
    description = models.TextField(blank=True,null=True)
    date = models.DateField()
    tags = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            is_payment = False
            if self.credit:
                installment = self.credit
                if installment:
                    installment.payed += self.amount
                    installment.payed_date = self.date
                    installment.save()
                    is_payment = True
            ## Account movement
            multiplicador = -1 if self.category.type == CategoryType.EXPENSE else 1
            monto_final = self.amount * multiplicador
            if is_payment:
                tipo_movimiento = MovementType.PY  # Pago de Deuda
            elif self.category.type == CategoryType.INCOME:
                tipo_movimiento = MovementType.TX  # Transfer
            else:
                tipo_movimiento = MovementType.EX  # Gasto común

            AccountMovement.objects.create(
                account=self.account,
                amount=-monto_final,
                reference=f"{self.reference} : {self.category.name}",
                tx_date=timezone.now(),
                mov_type=tipo_movimiento,
                created_by=self.created_by
            )
        

class ExpenseInvoice(BaseCreatedBy):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/%Y/%m/')


class AuthToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_tokens",
        on_delete=models.CASCADE,
    )
    key = models.CharField(max_length=64, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} {self.key[:8]}"