import abc


class ITerminalMode(abc.ABC):

    @abc.abstractmethod
    async def __call__(self):
        pass

    @abc.abstractmethod
    async def check(self):
        pass

    @abc.abstractmethod
    async def enter(self):
        pass

    @abc.abstractmethod
    async def exit(self):
        pass

    @abc.abstractmethod
    async def send_command(self, cmd):
        pass
