from enum import StrEnum


class APIResponseStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class BonusTaskType(StrEnum):
    TG_CHANNEL = "TG_CHANNEL"
    TG_BOT = "TG_BOT"
    UNSPECIFIED = "UNSPECIFIED"


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserFarmingStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class UserLanguage(StrEnum):
    RU = "RU"
    EN = "EN"
