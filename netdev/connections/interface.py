"""
Connection Interface
"""
import abc


class IConnection(abc.ABC):

    @abc.abstractmethod
    async def __aenter__(self):
        """Async Context Manager"""
        pass

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager"""
        pass

    @abc.abstractmethod
    def disconnect(self):
        """ Close Connection """
        pass

    @abc.abstractmethod
    def connect(self):
        """ Establish Connection """
        pass

    @abc.abstractmethod
    def send(self, cmd):
        """ send Command """
        pass

    @abc.abstractmethod
    def read(self):
        """ send Command """
        pass

    @abc.abstractmethod
    def read_until_pattern(self, pattern, re_flags=0):
        """ read util pattern """
        pass

    @abc.abstractmethod
    def read_until_prompt(self):
        """ read util pattern """
        pass

    @abc.abstractmethod
    def read_until_prompt_or_pattern(self, attern, re_flags=0):
        """ read util pattern """
        pass
