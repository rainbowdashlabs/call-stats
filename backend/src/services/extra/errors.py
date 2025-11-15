from fastapi import HTTPException
from pydantic import BaseModel


class ExistsError(HTTPException):
    def __init__(self, instance: BaseModel, message: str = None):
        if not message:
            message = type(instance).__name__ + " already exists"
        super().__init__(409, message)
        self.instance = instance


class NameExistsError(ExistsError):
    def __init__(self, instance: BaseModel):
        super().__init__(instance, type(instance).__name__ + " Name already exists")


class NotFoundError(HTTPException):
    def __init__(self, cls):
        super().__init__(404, cls.__name__ + " not found")

class IdChangeError(HTTPException):
    def __init__(self, cls):
        super().__init__(400, cls.__name__ + " id cannot be changed")