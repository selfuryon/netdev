import pytest

from netdev.vendors.cisco_like import CiscoTerminalModes, cisco_check_closure

check_func_data = [
    ("test-br-01>", CiscoTerminalModes.UNPRIVILEGE_EXEC),
    ("test-br-01#", CiscoTerminalModes.PRIVILEGE_EXEC),
    ("test-br-01(config)#", CiscoTerminalModes.CONFIG_MODE),
    pytest.param("test-br-01", 0, marks=pytest.mark.xfail)
]


@pytest.mark.asyncio
@pytest.mark.parametrize("buf,expected", check_func_data)
async def test_check_closure(buf, expected):
    check_func = cisco_check_closure(r">", r"#", r")#")
    result = await check_func(buf)
    assert result == expected
