from fastapi import HTTPException
from pydantic import BaseModel

_GERMAN_NAMES = {
    "Call": "Einsatz",
    "CreateCall": "Einsatz",
    "FullCall": "Einsatz",
    "Subject": "Stichwort",
    "SimpleSubject": "Stichwort",
    "Member": "Mitglied",
    "SimpleMember": "Mitglied",
    "MemberQualification": "Qualifikation",
    "Qualification": "Qualifikation",
    "Exercise": "Übung",
    "FullExercise": "Übung",
    "YouthExercise": "Jugendübung",
    "FullYouthExercise": "Jugendübung",
}


def german_name(cls) -> str:
    """Return the German label for an entity class, falling back to its class name."""
    return _GERMAN_NAMES.get(cls.__name__, cls.__name__)


class ExistsError(HTTPException):
    def __init__(self, instance: BaseModel, message: str = None):
        if not message:
            message = german_name(type(instance)) + " existiert bereits"
        super().__init__(409, message)
        self.instance = instance


class NameExistsError(ExistsError):
    def __init__(self, instance: BaseModel):
        super().__init__(instance, german_name(type(instance)) + ": Name existiert bereits")


class InUseError(HTTPException):
    """Raised when a record is still referenced elsewhere and has to be archived rather than deleted."""

    def __init__(self, cls, usage: str):
        super().__init__(409, german_name(cls) + " wird noch verwendet (" + usage + ") und kann nicht "
                              "gelöscht werden – bitte stattdessen archivieren")


class NotFoundError(HTTPException):
    def __init__(self, cls):
        super().__init__(404, german_name(cls) + " nicht gefunden")


class IdChangeError(HTTPException):
    def __init__(self, cls):
        super().__init__(400, "ID von " + german_name(cls) + " kann nicht geändert werden")
