#!/usr/bin/env -S pytest -v

import logging
log=logging.getLogger()
from ndom.dom.base.device import NetworkedInfrastructureDevice
from  ndom.dom.base.interface import Interface,InterfaceRange
import pytest


switch = NetworkedInfrastructureDevice(name="test")
switch.interfaces = InterfaceRange("ten1/1/1-48")

def test_interface_range_length():
    # 48 interfaces, 1 __type__ info
    assert len(list(switch.interfaces.keys())) == 49 

def test_interface_range_type():
    assert switch.interfaces["__type__"] == "InterfaceRange"

def test_interface_range_append():
    # 49 interfaces, 1 __type__ info
    switch.interfaces.append(Interface("ten2/1"))
    assert len(list(switch.interfaces.keys())) == 50
    
def test_interface_range_remove():
    # 49 interfaces, 1 __type__ info
    switch.interfaces.remove("ten2/1")
    assert len(list(switch.interfaces.keys())) == 49
    

def test_interface_range_attribute_on_creation():
    # 49 interfaces, 1 __type__ info
    switch = NetworkedInfrastructureDevice(name="test")
    switch.interfaces = InterfaceRange("ten1/1/1-48",speed=1000,status="up")
    with pytest.raises(AttributeError):
        assert switch.interfaces.speed == 1000
        assert switch.interfaces.status == "up"
        assert switch.interfaces["ten1/1/1"].status == "up"

    assert switch.interfaces["ten1/1/1"].speed == 1000
    assert switch.interfaces["ten1/1/48"].speed == 1000
    