from enum import IntFlag, _decompose, auto


class _BaseEnum(IntFlag):
    def __iter__(self):
        cls = self.__class__

        members, _ = _decompose(cls, self._value_)

        for m in members:
            yield str(m._name_ or m._value_)

    @classmethod
    def from_binary(cls, binary):
        return cls(int(binary, 2))


class LoggingEnum(_BaseEnum):
    NONE = auto()
    MESSAGE = auto()  # Message stuff
    CHANNELS = auto()  # Channel updating stuff
    GUILD = auto()  # Guild update, roles, etc
    MEMBER = auto()  # Member update,  roles added, nickname, etc
    MODERATION = auto()  # Bans, unbans, kicks


class AutomodEnum(_BaseEnum):
    """
    ATTRIBUTES:

    LINKS - Discord Links
    MENTIONS - Mass mentions, eg @everyone, @here, and num of mentions > 5

    """

    NONE = auto()
    LINKS = auto()  # Discord links
    MENTIONS = auto()  # Mass mentions, eg @everyone, @here, and num of mentions > 5
