from django.contrib import admin
from .models import (
    Team,
    TeamMember,
    Category,
    Account,
    AccountMovement,
    Budget,
    Credit,
    CreditInstallment,
    Expense,
    ExpenseInvoice,
    AuthToken,
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "members", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")
    readonly_fields = ("code", "created_at", "updated_at")
    ordering = ("name",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("member", "team", "is_team_owner", "account_limit", "created_by", "created_at")
    list_filter = ("is_team_owner", "team")
    search_fields = ("member__username", "member__email", "team__name", "team__code")
    list_select_related = ("member", "team", "created_by")
    autocomplete_fields = ("team", "member", "created_by")
    ordering = ("team", "member")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "type", "is_active", "icon", "color", "created_by")
    list_filter = ("type", "is_active", "team")
    search_fields = ("name", "description", "team__name")
    list_select_related = ("team", "created_by")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "currency", "opening_price", "limit_per_day", "is_active", "created_by")
    list_filter = ("currency", "is_active", "team")
    search_fields = ("name", "description", "team__name")
    list_select_related = ("team", "created_by")


@admin.register(AccountMovement)
class AccountMovementAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "mov_type", "tx_date", "reference", "created_by")
    list_filter = ("mov_type", "tx_date")
    search_fields = ("reference", "account__name")
    list_select_related = ("account", "created_by")
    date_hierarchy = "tx_date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "limit", "start_date", "end_date", "is_active", "created_by")
    list_filter = ("is_active", "team")
    search_fields = ("name", "description", "team__name")
    list_select_related = ("team", "created_by")
    date_hierarchy = "start_date"


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "team",
        "amount",
        "no_installments",
        "periodicity",
        "first_installment",
        "is_active",
        "created_by",
    )
    list_filter = ("is_active", "periodicity", "team")
    search_fields = ("name", "description", "team__name")
    list_select_related = ("team", "created_by")


@admin.register(CreditInstallment)
class CreditInstallmentAdmin(admin.ModelAdmin):
    list_display = ("credit", "number_in_year", "contract_year", "due_amout", "due_date", "payed", "payed_date")
    list_filter = ("contract_year", "due_date")
    search_fields = ("credit__name", "description")
    list_select_related = ("credit",)
    date_hierarchy = "due_date"


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("reference", "team", "account", "category", "amount", "date", "budget", "created_by")
    list_filter = ("date", "team", "category")
    search_fields = ("reference", "description", "tags", "team__name")
    list_select_related = ("team", "account", "category", "budget", "credit", "created_by")
    date_hierarchy = "date"


@admin.register(ExpenseInvoice)
class ExpenseInvoiceAdmin(admin.ModelAdmin):
    list_display = ("expense", "file", "created_by")
    search_fields = ("expense__reference",)
    list_select_related = ("expense", "created_by")


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "created_at")
    search_fields = ("user__username", "key")
    list_select_related = ("user",)
    readonly_fields = ("key", "created_at")
