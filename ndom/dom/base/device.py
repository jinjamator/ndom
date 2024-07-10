from .psu import PSUList
from .interface import InterfaceDict
from . import BaseFRU

class InfrastructureDevice(BaseFRU):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data["powersupplies"] = PSUList()


class NetworkedInfrastructureDevice(InfrastructureDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data["interfaces"] = InterfaceDict()


