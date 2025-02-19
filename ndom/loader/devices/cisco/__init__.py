from ...devices import DeviceLoader
from ...devices import ssh
from ....dom.devices.cisco.nxos import CiscoNXOSDevice
from ....dom.base.interface import InterfaceRange,Interface

import logging
import re

log = logging.getLogger()

# inventory_rgx={
#     "fex":{
#         "psu":r"FEX (?P<fex_id>\d+) Power Supply (?P<number>\d+)",
#         "fan":r"FEX (?P<fex_id>\d+) Fan (?P<number>)",
#         "chassis":r"FEX (?P<fex_id>\d+) CHASSIS",
#         "supervisor":r"FEX (?P<fex_id>\d+) Module 1",
#     },
#     "chassis"

# }


class CiscoDeviceLoader(DeviceLoader):
    def __init__(self, ip, username, password, platform, **kwargs):
        super().__init__(ip, username, password, platform, **kwargs)
        if platform.lower() in ["nxos", "nx-os", "cisco_nxos"]:
            self._platform = "cisco_nxos"
            self.dom = CiscoNXOSDevice(name=self.__get_hostname__())
            self.dom.interfaces = InterfaceRange()
            self.dom.interfaces+= Interface(_attrs=["name","speed","connector","hardware_type", "mgmt_only"],name="console", speed=9600, connector="rj45", hardware_type="serial")
            self.dom.interfaces+= Interface(name="mgmt0", speed=1000)

        # self.dom.configuration=self.__get_current_configuration__()

    def __str__(self):
        return str(self.dom)

    def __get_hostname__(self):
        return self._ip

    def __discover__(self):

        # for inventory_line in self.query("show inventory"):
        #     if "FEX" in inventory_line["name"]:
        #         # we dont do fex here
        #         continue
        #     if "Chassis" in inventory_line["name"]:
        #         self.dom.serial_number = inventory_line["sn"]
        #         self.dom.pid = inventory_line["pid"]
        

        # for module_line in self.query("show module"):
        #     self.dom.interfaces += InterfaceRange(
        #         f"Ethernet{module_line['module']}/1-{module_line['ports']}"
        #     )
        


        for interface in self.query("show interface"):
            rename=[
                ("admin_state","enabled"),
                ("address","mac_address"),
                ("bia","primary_mac_address"),
                ("interface","name"),
            ]
            replace_value = {
                "duplex": [
                    ("auto-duplex", {"value":"auto"} ),
                    ("full-duplex", {"value":"full"} ),
                    ("half-duplex", {"value":"half"} ),
                ],
                "speed": [
                    ("auto-speed", ""),
                    ("10 Mb/s",10000),
                    ("100 Mb/s",100000),
                    ("1000 Mb/s",1000000),
                    ("1 Gb/s",100000000),
                    ("10 Gb/s",1000000000),
                    ("25 Gb/s",2500000000),
                    ("40 Gb/s",4000000000),
                    ("50 Gb/s",5000000000),
                    ("100 Gb/s",10000000000),
                    ("200 Gb/s",20000000000),
                    ("400 Gb/s",40000000000),
                    ("800 Gb/s",80000000000),
                ],
                "encapsulation":[
                    ("802", "tagged"),
                    ("ARPA", "access"),
                ]
                
            }
              

            

            for ren in rename:
                interface[ren[1]]=interface[ren[0]]
                del interface[ren[0]]
            for var_name in replace_value:
                for repl in replace_value[var_name]:
                    if interface[var_name] == repl[0]:
                        interface[var_name]=repl[1]
                        break
            print(interface)
            # base, unit = interface["speed"].lower().split(" ")
            # base=int(base)
            # speed=0
            # match unit:
            #     case "mb/s": speed=base * 1000000
            #     case "gb/s": speed=base * 100000000
            #     case _: raise NotImplementedError(f"Speed unit {unit} not implemented")
            
            # interface["speed"]=speed

            interface["link_status"]=interface["link_status"].split(" ")[0]
            self.dom.interfaces += Interface(_attrs=interface.keys(),**interface)
            print(interface)
       
    def __get_current_configuration__(self):
        return ssh.run(
            "show running",
            device_type=self._platform,
            ip=self._ip,
            username=self._username,
            password=self._password,
        )
