from django.contrib.auth import authenticate
from ninja import Router
from ninja.errors import HttpError
from ninja.security import HttpBearer

from .models import AuthToken, Profile, TeamMember
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
    profile = Profile.objects.filter(user=user).first()
    teams = TeamMember.objects.filter(member=user)
    owner = teams.filter(is_team_owner=True).first()
    other_teams = teams.filter(is_team_owner=False).select_related("team")
    

    return UserOut(
        id = user.id, 
        username = user.username,
        email = user.email,
        name = profile.name if profile is not None else  '',
        surname = profile.surname if profile is not None else '',
        phone = profile.phone if profile is not None else '',
        team_code = owner.team.code if owner is not None else '',
        team_name = owner.team.name if owner is not None else '',
        other_teams=[membership.team.code for membership in other_teams]
    )
