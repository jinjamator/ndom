#!/usr/bin/env -S pytest -v

import logging

import ndom.renderer.base
log=logging.getLogger()
from ndom.dom.base.device import NetworkedInfrastructureDevice
from ndom.dom.base.interface import Interface,InterfaceRange
from ndom.renderer.base import BaseRenderer
from ndom.renderer.yaml import YAMLRenderer
from ndom.renderer.json import JSONRenderer


switch = NetworkedInfrastructureDevice(name="test")
switch.interfaces = InterfaceRange("ten1/1/1-48")






def test_base():
    printer=BaseRenderer()
    switch.add_render_plugin("print",printer)
    switch.render("print")

def test_json(tmp_path):
    d = tmp_path / "json"
    d.mkdir()
    p = d / "test.json"
    print(p)
    jsonwriter=JSONRenderer(path=str(p))
    switch.add_render_plugin("json",jsonwriter)
    switch.render("json")


def test_yaml(tmp_path):
    d = tmp_path / "yaml"
    d.mkdir()
    p = d / "test.yml"
    yamlwriter=YAMLRenderer(path=str(p))
    switch.add_render_plugin("yaml",yamlwriter)
    switch.render("yaml")
