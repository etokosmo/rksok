from models.model import add_user_to_db, get_phone_number_from_db, delete_user_from_db


def test_get_phone_number_from_db():
    assert get_phone_number_from_db("user", 1) is None
    assert get_phone_number_from_db("admin", 1) == "4444"


def test_add_user_to_db():
    assert add_user_to_db("qwerty", "123qwe", 1) is True


def test_delete_user_from_db():
    assert delete_user_from_db("zxc", 1) is False
    assert delete_user_from_db("qwerty", 1) is True
