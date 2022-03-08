import asyncio
import nest_asyncio
from loguru import logger
import socket
from typing import Optional, Union


def request_to_server_check(message: str, session: int) -> Union[str, bool]:
    """Request to server-check"""
    server_address = ('vragi-vezde.to.digital', 51624)
    try:
        client_socket = socket.create_connection(server_address, 5)  # connect to the server
        logger.info(f'Session: {session}. Send to server-check: {message!r}')
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024)  # receive response
        logger.info(f'Session: {session}. Response from server-check: {data.decode()!r}')
        response_from_check_server = data.decode()
        logger.info(f'Session: {session}. Close the connection with server-check')
        client_socket.close()  # close the connection
        return response_from_check_server
    except socket.gaierror:
        logger.debug(f'Session: {session}. FAIL: server-check is down')
        return False
    except TimeoutError:
        logger.debug(f'Session: {session}. FAIL: incorrect request to server-check')
        return False


def start_request_to_server_check(message: str, session: int) -> Optional[str]:
    """Request to the server-check about the possibility of processing the request"""
    message = 'АМОЖНА? РКСОК/1.0\r\n' + message
    # nest_asyncio.apply()
    # response = asyncio.run(request_to_server_check(message, session))
    response = request_to_server_check(message, session)
    if response:
        return response
    return None


# async def request_to_server_check(message: str, session: int) -> str:
#     reader, writer = await asyncio.open_connection(
#         'vragi-vezde.to.digital', 51624)
#
#     logger.info(f'Session: {session}. Send to server-check: {message!r}')
#     writer.write(message.encode())
#     await writer.drain()
#
#     data = await reader.read(100)
#     logger.info(f'Session: {session}. Response from server-check: {data.decode()!r}')
#
#     logger.info(f'Session: {session}. Close the connection with server-check')
#     writer.close()
#     await writer.wait_closed()
#     response_from_check_server = f'{data.decode()!r}'
#     return response_from_check_server