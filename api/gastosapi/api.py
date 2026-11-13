from ninja import NinjaAPI

from .auth import TokenAuth, router as auth_router
from .routers.accounts import movements_router, router as accounts_router
from .routers.budgets import router as budgets_router
from .routers.categories import router as categories_router
from .routers.credits import installments_router, router as credits_router
from .routers.expenses import invoices_router, router as expenses_router
from .routers.teams import members_router, router as teams_router

api = NinjaAPI(
    title="FinanzasNica API",
    version="1.0.0",
    description="API REST de gastosapi",
    auth=TokenAuth(),
)

api.add_router("/auth", auth_router)
api.add_router("/teams", teams_router)
api.add_router("/team-members", members_router)
api.add_router("/categories", categories_router)
api.add_router("/accounts", accounts_router)
api.add_router("/account-movements", movements_router)
api.add_router("/budgets", budgets_router)
api.add_router("/credits", credits_router)
api.add_router("/credit-installments", installments_router)
api.add_router("/expenses", expenses_router)
api.add_router("/expense-invoices", invoices_router)
