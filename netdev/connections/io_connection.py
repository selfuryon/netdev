"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

The module contains Abstract IO Connection Interface.
It's mandatory to use for all particular connection classes.

"""
import abc


class IOConnection(abc.ABC):
    """ Abstract IO Connection Interface """

    @abc.abstractmethod
    async def disconnect(self):
        """ Close connection """
        pass

    @abc.abstractmethod
    async def connect(self):
        """ Establish connection """
        pass

    @abc.abstractmethod
    def send(self, cmd):
        """ Send command to the channel """
        pass

    @abc.abstractmethod
    async def read(self):
        """ Read buffer from the channel """
        pass

    @property
    def host(self):
        """ Return the host address """
        pass
