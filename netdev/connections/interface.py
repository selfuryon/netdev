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
    async def disconnect(self):
        """ Close Connection """
        pass

    @abc.abstractmethod
    async def connect(self):
        """ Establish Connection """
        pass

    @abc.abstractmethod
    async def send(self, cmd):
        """ send Command """
        pass

    @abc.abstractmethod
    async def read(self):
        """ send Command """
        pass

    @abc.abstractmethod
    async def read_until_pattern(self, pattern, re_flags=0):
        """ read util pattern """
        pass

    @abc.abstractmethod
    async def read_until_prompt(self):
        """ read util pattern """
        pass

    @abc.abstractmethod
    async def read_until_prompt_or_pattern(self, attern, re_flags=0):
        """ read util pattern """
        pass
