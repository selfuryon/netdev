"""
Utilities Module.
"""
import re, os
from clitable import CliTable, CliTableError
from netdev.constants import CODE_SET, CODE_NEXT_LINE


def strip_ansi_escape_codes(string):
    """
    Remove some ANSI ESC codes from the output

    http://en.wikipedia.org/wiki/ANSI_escape_code

    Note: this does not capture ALL possible ANSI Escape Codes only the ones
    I have encountered

    Current codes that are filtered:
    ESC = '\x1b' or chr(27)
    ESC = is the escape character [^ in hex ('\x1b')
    ESC[24;27H   Position cursor
    ESC[?25h     Show the cursor
    ESC[E        Next line (HP does ESC-E)
    ESC[2K       Erase line
    ESC[1;24r    Enable scrolling from start to row end
    ESC7         Save cursor position
    ESC[r        Scroll all screen
    ESC8         Restore cursor position
    ESC[nA       Move cursor up to n cells
    ESC[nB       Move cursor down to n cells

    require:
        HP ProCurve
        F5 LTM's
        Mikrotik
    """

    output = string
    for ansi_esc_code in CODE_SET:
        output = re.sub(ansi_esc_code, "", output)

    # CODE_NEXT_LINE must substitute with '\n'
    output = re.sub(CODE_NEXT_LINE, "\n", output)

    return output


def get_template_dir():
    """Find and return the ntc-templates/templates dir."""
    try:
        template_dir = os.environ["NET_TEXTFSM"]
        index = os.path.join(template_dir, "index")
        if not os.path.isfile(index):
            # Assume only base ./ntc-templates specified
            template_dir = os.path.join(template_dir, "templates")
    except KeyError:
        # Construct path ~/ntc-templates/templates
        home_dir = os.path.expanduser("~")
        template_dir = os.path.join(home_dir, "ntc-templates", "templates")

    index = os.path.join(template_dir, "index")
    if not os.path.isdir(template_dir) or not os.path.isfile(index):
        msg = """
Valid ntc-templates not found, please install https://github.com/networktocode/ntc-templates
and then set the NET_TEXTFSM environment variable to point to the ./ntc-templates/templates
directory."""
        raise ValueError(msg)
    return template_dir


def clitable_to_dict(cli_table):
    """Converts TextFSM cli_table object to list of dictionaries."""
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)
    return objs


def get_structured_data(raw_output, platform, command):
    """Convert raw CLI output to structured data using TextFSM template."""
    template_dir = get_template_dir()
    index_file = os.path.join(template_dir, "index")
    textfsm_obj = CliTable(index_file, template_dir)
    attrs = {"Command": command, "Platform": platform}
    try:
        # Parse output through template
        textfsm_obj.ParseCmd(raw_output, attrs)
        structured_data = clitable_to_dict(textfsm_obj)
        output = raw_output if structured_data == [] else structured_data
        return output
    except CliTableError:
        return raw_output
