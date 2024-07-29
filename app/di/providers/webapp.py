from dishka import Provider, Scope, from_context, provide

from app.config import Config
from app.utils.auth import InitDataAuthManager


class WebAppProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def init_data_auth_manager(self, config: Config) -> InitDataAuthManager:
        return InitDataAuthManager(bot_token=config.app.telegram_bot_token)
