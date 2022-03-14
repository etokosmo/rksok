import re
from data.request_to_server_check import start_request_to_server_check
from models.model import add_user_to_db, get_phone_number_from_db, delete_user_from_db
from loguru import logger
from config import PATTERN, PROTOCOL, ResponseStatus, RequestVerb, END_OF_RESPONSE, IncorrectRequest
from dataclasses import dataclass


@dataclass
class ParseValues:
    username: str
    phone_number: str
    request_verb: str


def process_request(message: str, session: int) -> bytes:
    """Processing request"""
    try:
        client_parse_values = _parse_request(message, session)
        logger.info(f'Session: {session}. client_parse_values: {client_parse_values}')
        if response_from_server_check := _request_to_server_check(message, session):
            return f'{response_from_server_check}{END_OF_RESPONSE}'.encode()
        return _check_verb(client_parse_values, session)
    except IncorrectRequest:
        return f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()


def check_valid_request(header: str) -> bool:
    """Checking the correctness of the request"""
    try:
        header_pattern = re.match(PATTERN, header).group(0)
    except AttributeError:
        raise IncorrectRequest
    if header == header_pattern:
        return True
    return False


def _parse_request(message: str, session: int) -> ParseValues:
    """Parse request and get ParseValues"""
    data_message = message.rstrip().split('\r\n', maxsplit=1)
    header = data_message[0]
    try:
        phone_number = data_message[1]
    except IndexError:
        phone_number = ''
    if not check_valid_request(header):
        logger.info(f'Session: {session}. Check valid request. Incorrect request.')
        raise IncorrectRequest
    username = header.split()[1]
    request_verb = header.split()[0]
    return ParseValues(username=username, phone_number=phone_number, request_verb=request_verb)


def _request_to_server_check(message: str, session: int) -> str:
    """Request to server-check"""
    response_from_server_check = start_request_to_server_check(message, session)
    if response_from_server_check is None:
        logger.info(f'Session: {session}. Response_from_server_check is None. Incorrect request.')
        raise IncorrectRequest
    if response_from_server_check.split()[0] != ResponseStatus.POSSIBLE.value:
        logger.info(f'Session: {session}. Deny request from server.')
        logger.info(f'Session: {session}. Response: "{response_from_server_check}".')
        return response_from_server_check


def _check_verb(client_parse_values: ParseValues, session: int) -> bytes:
    """Check VERB and work with db"""
    username, phone_number, request_verb = client_parse_values.username, client_parse_values.phone_number, client_parse_values.request_verb
    if request_verb == RequestVerb.WRITE.value:
        if not phone_number:
            logger.info(f'Session: {session}. Not phone_number. Incorrect request.')
            raise IncorrectRequest
        logger.info(f'Session: {session}. VERB: "{RequestVerb.WRITE.value}".')
        if add_user_to_db(username, phone_number, session):
            logger.info(f'Session: {session}. Success: "{username}" added with phone_number "{phone_number}".')
            return f'{ResponseStatus.OK.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()

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
        raise IncorrectRequest
