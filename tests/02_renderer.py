import logging
log=logging.getLogger()
from ndom.dom.base.device import NetworkedInfrastructureDevice
from  ndom.dom.base.interface import InterfaceRange


switch = NetworkedInfrastructureDevice(name="test")
switch.interfaces = InterfaceRange("ten1/1/1-48")
