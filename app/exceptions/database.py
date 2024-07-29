from app.exceptions.base import BaseAPIError


class DatabaseError(BaseAPIError): ...


class IntegrityViolationError(DatabaseError):
    def __init__(self, object_name: str):
        super().__init__(f"Provided data of «{object_name}» violates integrity constraints")


class RecordNotFoundError(DatabaseError):
    def __init__(self, object_name: str):
        super().__init__(f"Record of «{object_name}» was not found")


class DBActionNotAllowedError(DatabaseError):
    def __init__(self, object_name: str):
        super().__init__(f"The following operation on «{object_name}» is currently not allowed!")
