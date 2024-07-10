


















# switch = NetworkedInfrastructureDevice(name="test")
# switch.serial_number = "KLUMP 234"
# switch.so_nicht = "oarsch"
# switch.add_attr("so_gehts", "hallo")
# print(switch)
# switch.so_gehts = "hihihi"
# switch.add_attrs(
#     {"entweder_so_list": ["mit", "defaults"]}, oder_so_geht_auch="str default"
# )
# print(switch)
# switch.entweder_so_list.append("haha")
# print(switch.powersupplies)
# switch.set_attrs(pid="asdf", vendor="citschgo")
# print(switch.get_attr("pid"))
# try:
#     print(switch.get_attr("gibts ned"))
# except AttributeError:
#     pass
# interface = Interface(name="1/1")
# interface2 = Interface(name="1/2")

# psu_1 = PSU(power=1000)
# psu_2 = PSU(power=1500)

# print(interface)
# switch.interfaces.append(interface)
# switch.interfaces.append(interface2)

# switch.powersupplies.append(psu_1)
# switch.powersupplies.append(psu_2)
# print(switch)
# print(switch.interfaces[0])


# switch2 = NetworkedInfrastructureDevice(name="test2")
# switch2.interfaces = InterfaceRange("e1/1-32", speed=1000)

