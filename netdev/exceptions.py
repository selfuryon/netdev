class DisconnectError(Exception):
    """AsyncSSH Disconnect Error with ip address"""

    def __init__(self, ip_address, code, reason):
        self.ip_address = ip_address
        self.code = code
        self.reason = reason
        self.msg = "Host {} Disconnect Error: {}".format(ip_address, reason)
        super().__init__(self.msg)


class TimeoutError(Exception):
    """concurrent.futures._base.TimeoutError with ip address"""

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.msg = "Host {} Timeout Error".format(ip_address)
        super().__init__(self.msg)


class CommitError(Exception):
    """concurrent.futures._base.TimeoutError with ip address"""

    def __init__(self, ip_address, reason):
        self.ip_address = ip_address
        self.reason = reason
        self.msg = "Host {} Commit Error: {}".format(ip_address, reason)
        super().__init__(self.msg)
