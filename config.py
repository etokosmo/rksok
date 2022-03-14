import os
from enum import Enum


BASE_DIR = os.path.dirname(__file__) or '.'
PATH_TO_DB = os.path.join(BASE_DIR, 'models', 'notebook.db')
PATH_TO_LOGS = os.path.join(BASE_DIR, 'logs', 'logs.log')


class IncorrectRequest(Exception):
    """Incorrect Request Exception"""
    pass


class RequestVerb(Enum):
    """Verbs specified in RKSOK specs for requests"""
    GET = "ОТДОВАЙ"
    DELETE = "УДОЛИ"
    WRITE = "ЗОПИШИ"


class ResponseStatus(Enum):
    """Response statuses specified in RKSOK specs for responses"""
    OK = "НОРМАЛДЫКС"
    NOTFOUND = "НИНАШОЛ"
    NOT_APPROVED = "НИЛЬЗЯ"
    INCORRECT_REQUEST = "НИПОНЯЛ"
    POSSIBLE = "МОЖНА"
    IMPOSSIBLE = "НИЛЬЗЯ"


PROTOCOL = "РКСОК/1.0"
END_OF_RESPONSE = "\r\n\r\n"
PATTERN = rf'({RequestVerb.GET.value}|{RequestVerb.DELETE.value}|{RequestVerb.WRITE.value}) (.{{3,30}}) {PROTOCOL}'


SERVER_IP = '0.0.0.0'
SERVER_PORT = 8888


SERVER_CHECK_DOMAIN = 'vragi-vezde.to.digital'
SERVER_CHECK_PORT = 51624