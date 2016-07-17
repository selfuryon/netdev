class DisconnectError(Exception):
    """AsyncSSH Disconnect Error with ip address"""
    def __init__(self, ip_address, code, reason):
        self.ip_address = ip_address
        self.code = code
        self.reason = reason
        self.msg = "Host {} Disconnect Error:{}".format(ip_address, reason)
        super().__init__(self.msg)


class PasswordChangeRequired(Exception):
    """AsyncSSH PasswordChangeRequired Error with ip address"""
    def __init__(self, ip_address, prompt):
        self.prompt = prompt
        self.msg = "Host {} Password change required:{}".format(ip_address, prompt)
        super().__init__(self.msg)


class BreakReceived(Exception):
    """AsyncSSH BreakReceived Error with ip address"""
    def __init__(self, ip_address, msec):
        self.msec = msec
        self.msg = "Host {} Break for {} msec".format(ip_address, msec)
        super().__init__(self.msg)


class SignalReceived(Exception):
    """AsyncSSH SignalReceived Error with ip address"""
    def __init__(self, ip_address, signal):
        self.signal = signal
        self.msg = "Host {} signal received:{}".format(ip_address, signal)
        super().__init__(self.msg)


class TerminalSizeChanged(Exception):
    """AsyncSSH TerminalSizeChanged Error with ip address"""
    def __init__(self, ip_address, width, height, pixwidth, pixheight):
        self.width = width
        self.height = height
        self.pixwidth = pixwidth
        self.pixheight = pixheight
        self.msg = "Host {} Terminal size changes:({},{},{},{})".format(ip_address, width, height, pixwidth, pixheight)
        super().__init__(self.msg)


class ChannelOpenError(Exception):
    """AsyncSSH ChannelOpenError Error with ip address"""
    def __init__(self, ip_address, code, reason):
        self.code = code
        self.reason = reason
        self.msg = "Host {} Channel open error:{}".format(ip_address, reason)
        super().__init__(self.msg)
