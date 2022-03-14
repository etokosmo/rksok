from loguru import logger
import socket
from typing import Optional, Union
from config import SERVER_CHECK_DOMAIN, SERVER_CHECK_PORT


def socket_receive(sock) -> Optional[bytes]:
    """Reading data from socket"""
    msg = b''
    while True:
        chunk = sock.recv(1024)
        if chunk == '':
            raise RuntimeError("broken")
        msg = msg + chunk
        if b'\r\n\r\n' in msg:
            break
    return msg


def socket_send(sock, msg) -> None:
    """Send data to socket"""
    total_sent = 0
    while total_sent < len(msg):
        sent = sock.send(msg[total_sent:])
        if sent == 0:
            raise RuntimeError("broken")
        total_sent = total_sent + sent


def request_to_server_check(message: str, session: int) -> Union[str, bool]:
    """Request to server-check"""
    server_address = (SERVER_CHECK_DOMAIN, SERVER_CHECK_PORT)
    try:
        client_socket = socket.create_connection(server_address, 10)  # connect to the server
        logger.info(f'Session: {session}. Send to server-check: {message!r}')
        socket_send(client_socket, message.encode()) # send message
        data = socket_receive(client_socket) # receive response
        logger.info(f'Session: {session}. Response from server-check: {data.decode()!r}')
        response_from_check_server = data.decode()
        logger.info(f'Session: {session}. Close the connection with server-check')
        client_socket.close()  # close the connection
        return response_from_check_server
    except socket.gaierror:
        logger.debug(f'Session: {session}. FAIL: server-check is down')
        return False
    except TimeoutError:
        logger.debug(f'Session: {session}. FAIL: incorrect request to server-check. TimeoutError')
        return False
    except RuntimeError:
        logger.debug(f'Session: {session}. FAIL: incorrect request to server-check. Runtime error')
        return False


def start_request_to_server_check(message: str, session: int) -> Optional[str]:
    """Request to the server-check about the possibility of processing the request"""
    message = 'АМОЖНА? РКСОК/1.0\r\n' + message
    response = request_to_server_check(message, session)
    if response:
        return response
    return None

