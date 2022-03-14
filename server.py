import asyncio
from dataclasses import dataclass
from data.processing_request import process_request
from loguru import logger
from config import PATH_TO_LOGS, ResponseStatus, PROTOCOL, END_OF_RESPONSE, SERVER_IP, SERVER_PORT


async def rksok_server(reader: asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter):
    """Open connection - work with client - close connection"""
    try:
        data = await asyncio.wait_for(get_request(reader), timeout=20)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        logger.info(f'Session: {ClientNumber.current_client_number} from {addr!r}')
        response = process_request(message, ClientNumber.current_client_number)
        ClientNumber.current_client_number += 1
        writer.write(response)
        await writer.drain()
    except asyncio.TimeoutError:
        logger.debug(f'Session: {ClientNumber.current_client_number}. Timeout or another error')
        data = f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        writer.write(data)
        await writer.drain()
    except AttributeError:
        logger.debug(f'Session: {ClientNumber.current_client_number}. AttributeError')
        data = f'{ResponseStatus.INCORRECT_REQUEST.value} {PROTOCOL}{END_OF_RESPONSE}'.encode()
        writer.write(data)
        await writer.drain()
    finally:
        logger.info(f'Session: {ClientNumber.current_client_number}. Close the connection')
        writer.close()


async def get_request(reader: asyncio.streams.StreamReader) -> bytes:
    """Get data from client"""
    data = b''
    while True:
        temp = await reader.read(1024)
        if not temp: break
        data += temp
        if data.endswith(END_OF_RESPONSE.encode()):
            return data


async def main():
    """Start server"""
    server = await asyncio.start_server(
        rksok_server, SERVER_IP, SERVER_PORT)
    async with server:
        await server.serve_forever()


@dataclass
class ClientNumber:
    current_client_number: int = 1


logger.add(PATH_TO_LOGS, level='DEBUG')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug(f'Forced Server Shutdown')
