#!/usr/bin/env -S pytest -v -rP

import logging
import os
import ndom.renderer.base
from getpass import getpass

log=logging.getLogger()
log.setLevel(logging.DEBUG)
from ndom.loader.devices.cisco import CiscoDeviceLoader
from ndom.dom.devices.cisco.nxos import CiscoNXOSDevice

nxos_host=os.environ.get("NDOM_NXOS_TEST_HOST","100.76.0.1")
nxos_user=os.environ.get("NDOM_NXOS_TEST_USERNAME","admin")
nxos_password=os.environ.get("NDOM_NXOS_TEST_PASSWORD",False) or getpass("NDOM_NXOS_TEST_PASSWORD:")


def test_base():
    device=CiscoDeviceLoader(nxos_host,nxos_user,nxos_password,"cisco_nxos",persistent_cache_basedir="/home/putzw/.ndom/",persistent_cache_lifetime=3600*24*30)
    device.load()
    print(device)
