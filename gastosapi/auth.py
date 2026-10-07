from django.contrib.auth import authenticate
from ninja import Router
from ninja.errors import HttpError
from ninja.security import HttpBearer

from .models import AuthToken
from .schemas import LoginIn, TokenOut, UserOut


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            return AuthToken.objects.select_related("user").get(key=token).user
        except AuthToken.DoesNotExist:
            return None


router = Router(tags=["Auth"])


@router.post("/login", response=TokenOut, auth=None)
def login(request, payload: LoginIn):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None or not user.is_active:
        raise HttpError(401, "Credenciales inválidas")
    token = AuthToken.objects.create(user=user)
    return TokenOut(token=token.key)


@router.post("/logout")
def logout(request):
    header = request.headers.get("Authorization", "")
    key = header.removeprefix("Bearer ").strip()
    AuthToken.objects.filter(user=request.auth, key=key).delete()
    return {"ok": True}


@router.get("/me", response=UserOut)
def me(request):
    user = request.auth
    return UserOut(id=user.id, username=user.username, email=user.email)
