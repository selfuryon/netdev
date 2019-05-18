"""
Constants Module
"""
# Session Terminal Const.
TERM_WID = 2147483647
TERM_LEN = 2147483647
TERM_TYPE = 'vt100'

# ansi codes
CODE_SAVE_CURSOR = chr(27) + r"7"
CODE_SCROLL_SCREEN = chr(27) + r"\[r"
CODE_RESTORE_CURSOR = chr(27) + r"8"
CODE_CURSOR_UP = chr(27) + r"\[\d+A"
CODE_CURSOR_DOWN = chr(27) + r"\[\d+B"

CODE_POSITION_CURSOR = chr(27) + r"\[\d+;\d+H"
CODE_SHOW_CURSOR = chr(27) + r"\[\?25h"
CODE_NEXT_LINE = chr(27) + r"E"
CODE_ERASE_LINE = chr(27) + r"\[2K"
CODE_ENABLE_SCROLL = chr(27) + r"\[\d+;\d+r"

CODE_SET = [
    CODE_SAVE_CURSOR,
    CODE_SCROLL_SCREEN,
    CODE_RESTORE_CURSOR,
    CODE_CURSOR_UP,
    CODE_CURSOR_DOWN,
    CODE_POSITION_CURSOR,
    CODE_SHOW_CURSOR,
    CODE_ERASE_LINE,
    CODE_ENABLE_SCROLL,
]