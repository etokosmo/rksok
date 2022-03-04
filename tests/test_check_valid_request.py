from data.processing_request import check_valid_request


def test_check_valid_request():
    assert check_valid_request("ЗОПИШИ Иван Хмурый РКСОК/1.0") is True
    assert check_valid_request("УДОЛИ имя РКСОК/1.0") is True
    assert check_valid_request("ОТДОВАЙ имя РКСОК/1.0") is True
    assert check_valid_request("ЗАПИШИ qwerty01 РКСОК/1.0") is False
    assert check_valid_request("ЗОПИШИ 0123456789012345678901234567890123456789 РКСОК/1.0") is False
    assert check_valid_request("ЗОПИШИ Иван Хмурый РКСОК/1.0asd") is False
