import pytest

from netdev.vendors.cisco_like import (CiscoCLIModes, cisco_check_closure,
                                       cisco_set_prompt_closure)

check_data = [
    ("test-br-01>", CiscoCLIModes.UNPRIVILEGE_EXEC),
    ("test-br-01#", CiscoCLIModes.PRIVILEGE_EXEC),
    ("test-br-01(config)#", CiscoCLIModes.CONFIG),
    pytest.param("test-br-01", 0, marks=pytest.mark.xfail),
]

set_prompt_data = [
    ("test-br-01>", "test-br-01(\\(.*?\\))?[>|\\#]"),
    ("test-br-01#", "test-br-01(\\(.*?\\))?[>|\\#]"),
    pytest.param("test-br-01", 0, marks=pytest.mark.xfail),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("buf,expected", check_data)
async def test_check_closure(buf, expected):
    check_func = cisco_check_closure(r">", r"#", r")#")
    result = await check_func(buf)
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("buf,expected", set_prompt_data)
async def test_set_prompt_closure(buf, expected):
    set_prompt_func = cisco_set_prompt_closure([r">", r"#"])
    result = set_prompt_func(buf)
    assert result == expected
