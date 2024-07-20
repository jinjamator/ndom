#!/usr/bin/env -S pytest -v

import logging
log=logging.getLogger()
from ndom.dom.base.device import NetworkedInfrastructureDevice
from  ndom.dom.base.interface import Interface,InterfaceRange,BreakoutInterface



def test_networked_infrastructure_device_attribute_on_creation_name():
    switch = NetworkedInfrastructureDevice(name="karlheinz")
    assert switch.name == "karlheinz" 

