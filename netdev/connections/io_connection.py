"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

The module contains Abstract IO Connection Interface.
It's mandatory to use for all particular connection classes.

"""
import abc


class IOConnection(abc.ABC):
    """ Abstract IO Connection Interface """

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """ Close connection """

    @abc.abstractmethod
    async def connect(self) -> None:
        """ Establish connection """

    @abc.abstractmethod
    async def send(self, cmd: str) -> None:
        """ Send command to the channel """

    @abc.abstractmethod
    async def read(self) -> str:
        """ Read buffer from the channel """

    @property
    def host(self) -> str:
        """ Return the host address """
