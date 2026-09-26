from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja_jwt.authentication import AsyncJWTAuth

router = Router(tags=["auth"])
User = get_user_model()

class UserOut(Schema):
    id: int
    username: str
    email: str


class RegisterIn(Schema):
    username: str
    email: str
    password: str


class Login(Schema):
    username: str
    password: str

@router.post("/login", response=UserOut)
def login(request, payload: Login):
    user = User.objects.filter(username__iexact=payload.username).first()
    if not user or not user.check_password(payload.password):
        raise HttpError(400, "Invalid username or password")
    return user

@router.post("/register", response={201: UserOut})
def register(request, payload: RegisterIn):
    if User.objects.filter(username__iexact=payload.username).exists():
        raise HttpError(400, "Username already taken")
    if User.objects.filter(email__iexact=payload.email).exists():
        raise HttpError(400, "Email already registered")
    try:
        validate_password(payload.password)
    except ValidationError as e:
        raise HttpError(400, " ".join(e.messages))

    return 201, User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )
@router.get("/me", auth=AsyncJWTAuth(), response=UserOut)
def me(request):
    return request.auth