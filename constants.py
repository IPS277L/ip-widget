from enum import Enum

from ip_services import FreeIPAPI, IP2Location


class IPServices(Enum):
    FreeIPAPI = FreeIPAPI
    IP2Location = IP2Location
