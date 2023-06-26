from enum import Enum


class DeviceType(str, Enum):
    SERVICE = "service"
    TARGET = "target"

    def __str__(self) -> str:
        return str(self.value)
