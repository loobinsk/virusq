from dishka import Provider, Scope, provide, from_context

from app.config import Config
from app.utils.auth import JWTAuth


class JWTManagerProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config, scope=Scope.APP)
    jwt_manager = from_context(provides=JWTAuth, scope=Scope.APP)

    @provide
    def get_jwt_manager(self, jwt_manager: JWTAuth) -> JWTAuth:
        return jwt_manager
