import asyncio
from dataclasses import dataclass
from data.processing_request import processing_request
from loguru import logger
from config import path_to_logs
from data.processing_request import ResponseStatus, PROTOCOL, END_OF_RESPONSE
logger.add(path_to_logs, level='DEBUG')


async def handle_echo(reader, writer):
    """Open connection - work with client - close connection"""
    try:
        data = await asyncio.wait_for(get_request(reader), timeout=5)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        logger.info(f'Session: {Logs.current_session_position} from {addr!r}')
        response = processing_request(message, Logs.current_session_position)
        writer.write(response)
        await writer.drain()
    except asyncio.TimeoutError:
        logger.debug(f'Session: {Logs.current_session_position}. Timeout or another error')
        data = f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        writer.write(data)
        await writer.drain()
    except AttributeError:
        logger.debug(f'Session: {Logs.current_session_position}. AttributeError')
        data = f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        writer.write(data)
        await writer.drain()
    finally:
        logger.info(f'Session: {Logs.current_session_position}. Close the connection')
        writer.close()
        Logs.current_session_position += 1


async def get_request(reader):
    """Get data from client"""
    data = b''
    while True:
        temp = await reader.read(1024)
        if not temp: break
        data += temp
        if b'\r\n\r\n' in data:
            return data


async def main():
    """Start server"""
    server = await asyncio.start_server(
        handle_echo, '0.0.0.0', 8888)
    async with server:
        await server.serve_forever()


@dataclass
class Logs:
    current_session_position: int = 1


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug(f'Forced Server Shutdown')
