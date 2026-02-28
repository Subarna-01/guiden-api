import jwt
import datetime
from fastapi.security import HTTPBearer
from app.core.settings import settings

auth_scheme = HTTPBearer()


class Jwt:
    def create_access_token(
        self, payload: dict, expires_delta: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ) -> str:
        to_encode = payload.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=expires_delta
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def create_refresh_token(
        self, payload: dict, expires_delta: int = settings.REFRESH_TOKEN_EXPIRE_DAYS
    ) -> str:
        to_encode = payload.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=expires_delta
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def decode_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
