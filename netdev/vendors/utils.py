"""
utils module
"""
import os
from netdev._textfsm import _clitable as clitable


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


def textfasm_parser(raw_output, command, device_type):
    """Convert raw CLI output to Dict using TextFSM template."""
    template_dir = get_template_dir()
    index_file = os.path.join(template_dir, "index")
    textfsm_obj = clitable.CliTable(index_file, template_dir)
    attrs = {"Command": command, "Platform": device_type}
    try:
        # Parse output through template
        textfsm_obj.ParseCmd(raw_output, attrs)
        structured_data = clitable_to_dict(textfsm_obj)
        output = raw_output if structured_data == [] else structured_data
        return output
    except clitable.CliTableError:
        return raw_output
