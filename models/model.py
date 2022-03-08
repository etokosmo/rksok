import sqlite3
from sqlite3 import Error
from typing import Optional
from loguru import logger
from config import path_to_db
import os.path


def check_not_table_in_db() -> bool:
    """Checking if a table NOT exists in a database."""
    if os.path.getsize(path_to_db) == 0:
        return True
    return False


def _create_connection(path) -> sqlite3.Connection:
    """Connection to SQLite DB"""
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.info(f'Connection to SQLite DB successful')
    except Error as e:
        logger.debug(f"The error '{e}' occurred")
    return connection


def _execute_query(connection, query, session: int) -> None:
    """Request to DB (CREATE, INSERT, UPDATE, DELETE)"""
    logger.info(f'Session: {session}. Request to DB')
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logger.info(f'Query executed successfully')
    except Error as e:
        logger.debug(f"The error '{e}' occurred")


def _execute_read_query(connection, query, session: int):
    logger.info(f'Session: {session}. Request to DB')
    """Request to DB (Only SELECT)"""
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        logger.debug(f"The error '{e}' occurred")


def _create_table() -> None:
    """Create table"""
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone_number TEXT
    );
    """
    _execute_query(connection, create_users_table, session=0)


def add_user_to_db(username: str, phone_number: str, session: int) -> bool:
    """Add username and phone_number to DB"""
    if check_user_in_db(username, session):
        _update_user_phone_number(username, phone_number, session)
    else:
        add_user = f"""
        INSERT INTO
          users (name, phone_number)
        VALUES
          ('{username}', '{phone_number}')
        ;
        """
        _execute_query(connection, add_user, session)
    return True


def get_phone_number_from_db(username: str, session: int) -> Optional[str]:
    """Get phone_number using user"""
    if check_user_in_db(username, session):
        select_user = f"SELECT phone_number from users WHERE name = '{username}'"
        selected_user = _execute_read_query(connection, select_user, session)
        return selected_user[0][0]
    return None


def _update_user_phone_number(username: str, phone_number: str, session: int) -> None:
    """Update phone_number using username"""
    update_user_description = f"""
    UPDATE
      users
    SET
      phone_number = '{phone_number}'
    WHERE
      name = '{username}'
    """
    _execute_query(connection, update_user_description, session)


def check_user_in_db(username: str, session: int) -> bool:
    """Check user in DB using username"""
    select_user = f"SELECT name from users WHERE name = '{username}'"
    selected_user = _execute_read_query(connection, select_user, session)
    if selected_user:
        logger.info(f'Session: {session}. SUCCESS: Check user in DB')
        return True
    logger.info(f'Session: {session}. FAIL: Check user in DB')
    return False


def get_users() -> list:
    """Return list of DB"""
    select_user = f"SELECT * from users"
    selected_user = _execute_read_query(connection, select_user, 0)
    return selected_user


def delete_user_from_db(username: str, session: int) -> bool:
    """Delete user from DB using username"""
    if check_user_in_db(username, session):
        delete_comment = f"DELETE FROM users WHERE name = '{username}'"
        _execute_query(connection, delete_comment, session)
        return True
    return False


connection = _create_connection(path_to_db)
if check_not_table_in_db():
    _create_table()
