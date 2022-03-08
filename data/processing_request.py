from enum import Enum
import re
from data.request_to_server_check import start_request_to_server_check
from models.model import add_user_to_db, get_phone_number_from_db, delete_user_from_db
from loguru import logger


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


PATTERN = rf'({RequestVerb.GET.value}|{RequestVerb.DELETE.value}|{RequestVerb.WRITE.value}) (.{{3,30}}) (РКСОК\/1\.0)'
PROTOCOL = "РКСОК/1.0"
END_OF_RESPONSE = "\r\n\r\n"


def cut_request(message: str) -> str:
    """Trim the message to remove unnecessary"""
    data, separator, trash = message.partition('\r\n\r\n')
    return data + separator


def check_valid_request(header: str) -> bool:
    """Checking the correctness of the request"""
    try:
        header_pattern = re.match(PATTERN, header).group(0)
        if header == header_pattern:
            return True
        return False
    except AttributeError:
        return False


def processing_request(message: str, session: int) -> bytes:
    """Processing request"""
    message = cut_request(message)
    data_message = message.rstrip().split('\r\n', maxsplit=1)
    header = data_message[0]
    if not check_valid_request(header):
        logger.info(f'Session: {session}. Incorrect request.')
        return f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
    username = header.split()[1]
    response_from_server_check = start_request_to_server_check(message, session)
    if response_from_server_check is None:
        return f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
    if response_from_server_check.split()[0] != ResponseStatus.POSSIBLE.value:
        logger.info(f'Session: {session}. Deny request from server.')
        logger.info(f'Session: {session}. Response: "{response_from_server_check}".')
        return f'{response_from_server_check}{END_OF_RESPONSE}'.encode()
    request_verb = header.split()[0]
    if request_verb == RequestVerb.WRITE.value:
        logger.info(f'Session: {session}. VERB: "{RequestVerb.WRITE.value}".')
        try:
            phone_number = data_message[1]
            if add_user_to_db(username, phone_number, session):
                logger.info(f'Session: {session}. Success: "{username}" added with phone_number "{phone_number}".')
                return f'{ResponseStatus.OK.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        except IndexError:
            logger.info(f'Session: {session}. Incorrect request.')
            return f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()

    elif request_verb == RequestVerb.GET.value:
        logger.info(f'Session: {session}. VERB: "{RequestVerb.GET.value}".')
        phone_number = get_phone_number_from_db(username, session)
        if phone_number is None:
            logger.info(f'Session: {session}. FAIL: "{username}" not found.')
            return f'{ResponseStatus.NOTFOUND.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        logger.info(f'Session: {session}. Success: Got phone_number "{phone_number}" from user "{username}".')
        return f'{ResponseStatus.OK.value} {PROTOCOL}\r\n{phone_number}{END_OF_RESPONSE}'.encode()

    elif request_verb == RequestVerb.DELETE.value:
        logger.info(f'Session: {session}. VERB: "{RequestVerb.DELETE.value}".')
        if delete_user_from_db(username, session):
            logger.info(f'Session: {session}. Success: Delete user "{username}".')
            return f'{ResponseStatus.OK.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        logger.info(f'Session: {session}. FAIL: "{username}" not found.')
        return f'{ResponseStatus.NOTFOUND.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()

    else:
        logger.debug(f'Session: {session}. Incorrect VERB.')
        return f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
