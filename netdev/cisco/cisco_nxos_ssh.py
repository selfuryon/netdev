import re

from netdev.netdev_base import NetDevSSH


class CiscoNxosSSH(NetDevSSH):
    @staticmethod
    def _normalize_linefeeds(a_string):
        """
        Convert '\r\n' or '\r\r\n' to '\n, and remove extra '\r's in the text
        """

        newline = re.compile(r'(\r\r\n|\r\n)')

        return newline.sub('\n', a_string).replace('\r', '')
