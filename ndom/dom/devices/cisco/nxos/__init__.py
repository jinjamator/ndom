from .. import CiscoDevice

class CiscoNXOSDevice(CiscoDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vendor="cisco"
        
    