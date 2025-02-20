#!/usr/bin/env -S pytest -v -rP

import logging

import ndom.renderer.base
log=logging.getLogger()
from ndom.dom.base.device import NetworkedInfrastructureDevice
from ndom.dom.base.interface import Interface,InterfaceRange
from ndom.renderer.base import BaseRenderer
from ndom.renderer.yaml import YAMLRenderer
from ndom.renderer.json import JSONRenderer
from ndom.loader.json import JSONLoader
from ndom.loader.yaml import YAMLLoader



switch = NetworkedInfrastructureDevice(name="test")
switch.interfaces = InterfaceRange("ten1/1/1-3",speed=1000,status="down",admin_status="up")
switch.interfaces.append(InterfaceRange("ten1/1/4-8",speed=25000,status="down",admin_status="up"))
switch.interfaces+=InterfaceRange("ten1/1/9-10",speed=100000,status="down",admin_status="up")
switch.interfaces.append("ten1/1/11",speed=25000,status="down",admin_status="up")
switch.interfaces+=InterfaceRange("ten1/1/12",speed=25000,status="down",admin_status="up")
switch.interfaces+=Interface(name="ten1/1/13",speed=25000,status="down",admin_status="up")


def test_base():
    printer=BaseRenderer()
    switch.add_render_plugin("print",printer)
    switch.render("print")

def test_json(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    p = str(tmp_path / "test.json")
    p2 = str(tmp_path / "test2.json")
    jsonwriter=JSONRenderer(path=str(p))
    jsonwriter2=JSONRenderer(path=str(p2))
    switch.add_render_plugin("json",jsonwriter)
    switch.render("json")

    loader=JSONLoader(p)
    obj=loader.load(p)
    obj.add_render_plugin("json2",jsonwriter2)
    obj.render("json2")

    with open(p,"r") as fh:
        d1=fh.read()
    with open(p2,"r") as fh:
        d2=fh.read()

    assert d1 == d2 
    
def test_yaml(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    p = str(tmp_path / "test.yaml")
    p2 = str(tmp_path / "test2.yaml")
    yamlwriter=YAMLRenderer(path=str(p))
    yamlwriter2=YAMLRenderer(path=str(p2))
    switch.add_render_plugin("yaml",yamlwriter)
    switch.render("yaml")

    loader=YAMLLoader(p)
    obj=loader.load(p)
    obj.add_render_plugin("yaml2",yamlwriter2)
    obj.render("yaml2")

    with open(p,"r") as fh:
        d1=fh.read()
    with open(p2,"r") as fh:
        d2=fh.read()

    assert d1 == d2 
    






# def test_yaml(tmp_path):
#     tmp_path.mkdir(exist_ok=True)
#     p = str(tmp_path / "test.yml")
#     yamlwriter=YAMLRenderer(path=str(p))
#     switch.add_render_plugin("yaml",yamlwriter)
#     switch.render("yaml")
