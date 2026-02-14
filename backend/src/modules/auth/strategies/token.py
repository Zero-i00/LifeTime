import jwt
import uuid
from config import settings
from datetime import datetime, timedelta, timezone


class TokenStrategy:

    @staticmethod
    def encode_jwt(
            payload: dict,
            private_key: str = settings.auth.private_key_path.read_text(),
            algorithm: str = settings.auth.algorithm,
            expire_minutes: int = settings.auth.access_token_expire_minutes,
            expire_timedelta: timedelta | None = None
    ):
        now = datetime.now(timezone.utc)
        to_encode = payload.copy()

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)

        to_encode.update(
            iat=int(now.timestamp()),
            exp=int(expire.timestamp()),
            jti=str(uuid.uuid4())
        )

        return jwt.encode(to_encode, private_key, algorithm=algorithm)

    @staticmethod
    def decode_jwt(
            token: str | bytes,
            algorithm: str = settings.auth.algorithm,
            public_key: str = settings.auth.public_key_path.read_text(),
    ):
        return jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])


token_strategy = TokenStrategy()
