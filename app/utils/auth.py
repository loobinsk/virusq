import hashlib
import hmac
import os
from binascii import Error
from datetime import timedelta
from typing import Dict, Type

from cryptography.fernet import Fernet, InvalidToken
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Security, HTTPException
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase
from fastapi_jwt.jwt import JwtAuthBase, JwtAccess
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.config import config
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.schemas.base import BaseChecksumEntity
from app.schemas.general.auth import JWTParsedData, JWTValidationData, JWTExtraData

CHECK_INIT_DATA = int(os.getenv("CHECK_INIT_DATA", 0))


class InitDataAuthManager:
    def __init__(self, bot_token: str):
        self.__bot_token = bot_token

    def check_hash(self, init_data: Dict[str, str]) -> bool:
        c_str = b"WebAppData"

        sorted_items = sorted(init_data.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items if k != "hash")

        secret_key = hmac.new(c_str, self.__bot_token.encode(), hashlib.sha256).digest()

        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if CHECK_INIT_DATA:
            return h == init_data["hash"]
        return True


class JWTAuth(JwtAccess):
    def __init__(
        self,
        secret_key: str,
        auto_error: bool = True,
        algorithm: str | None = None,
        access_expires_delta: timedelta | None = None,
        skip_serialization: bool = False,
    ):
        if not access_expires_delta:
            access_expires_delta = timedelta(weeks=4 * 12 * 10)  # expires in 10 years

        self.skip_serialization = skip_serialization

        super().__init__(
            secret_key=secret_key,
            places={"header"},
            auto_error=auto_error,
            algorithm=algorithm,
            access_expires_delta=access_expires_delta,
        )

    @inject
    async def __call__(
        self,
        user_repo: FromDishka[UserRepository],
        uow: FromDishka[BaseUoW],
        bearer: JwtAuthBase.JwtAccessBearer = Security(JwtAccess._bearer),
    ) -> JWTValidationData | None:
        raw_jwt_data = await self._get_credentials(bearer=bearer, cookie=None)

        if self.skip_serialization:
            return None

        user = await user_repo.get_by_id(model_id=raw_jwt_data.subject["user_id"])  # type: ignore[union-attr]
        if not user or user.is_banned:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Access denied")

        await user_repo.renew_last_activity_at(model_id=raw_jwt_data.subject["user_id"])  # type: ignore[union-attr]
        await uow.commit()

        return JWTValidationData(
            parsed_data=JWTParsedData.parse_obj(raw_jwt_data.subject),  # type: ignore[union-attr]
            extra_data=JWTExtraData(user=user),
        )


class ChecksumAuth(APIKeyBase):
    CHECKSUM_FIELD_NAME = "checksum"

    def __init__(
        self,
        auth_data_model: Type[BaseChecksumEntity],
        name: str,
        description: str,
    ):
        self.model: APIKey = APIKey(
            **{"in": APIKeyIn.cookie},  # type: ignore[arg-type]
            name=name,
            description=description,
        )
        self.auth_data_model = auth_data_model
        self.scheme_name = "Checksum Cookie"

    async def __call__(self, request: Request) -> None:
        json_data = await request.json()
        checksum = json_data.get(self.CHECKSUM_FIELD_NAME)

        try:
            raw_decoded_checksum = self.__decode_checksum(checksum)
        except (InvalidToken, TypeError, Error):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Access Forbidden",
            )
        return self.auth_data_model.from_decoded_checksum(raw_decoded_checksum)

    def __decode_checksum(self, checksum: str) -> str:
        return Fernet(config.app.game_checksum_secret_key).decrypt(checksum).decode("utf-8")
