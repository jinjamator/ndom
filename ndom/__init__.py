from collections import UserList, UserDict
import json
from copy import deepcopy
import logging

log=logging.getLogger(__file__)

class AttributeExistsError(BaseException):
    pass


class AutoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if FRUBaseDict in obj.__class__.__bases__:
            return obj.data
        if FRUBaseList in obj.__class__.__bases__:
            return obj.data
        if BaseFRU in obj.__class__.__bases__:
            return obj._data
        return json.JSONEncoder.default(self, obj)


""


class BaseFRU(object):

    def __init__(self, *args, **kwargs) -> None:
        self._parent = None
        self._renderer_list=[]
        self._data = {}
        self._attrs = kwargs.get(
            "_attrs",
            [
                "id",
                "name",
                "vendor",
                "pid",
                "serial_number",
                "type",
                ("capabilities", ()),
            ],
        )
        for attr in self._attrs:
            if isinstance(attr, tuple):
                if isinstance(attr[1], tuple):
                    list(attr[1])
                self._data[attr[0]] = kwargs.get(attr, deepcopy(attr[1]))
            else:
                self._data[attr] = kwargs.get(attr, None)
        self._data["type"] = str(self.__class__.__name__)

    def __repr__(self):
        return json.dumps(self._data, cls=AutoJsonEncoder, indent=2, sort_keys=False)

    def __getattr__(self, name: str):
        if name in self._data:
            return self._data[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value) -> None:
        if name in ["_data", "_parent","_renderer_list"]:
            super().__setattr__(name, value)
        # we do not implicitly create attributes by access for now
        elif name in self._data:
            self._data[name] = value
        else:
            super().__setattr__(name, value)

    def add_attr(self, name, default=None):
        if name in self._data:
            raise AttributeExistsError(
                f"cannot add already existing attribute {name} to {self.__class__.__name__}"
            )
        self._attrs.append((name, default))
        self._data[name] = default

    def add_attrs(self, new_attrs={}, **kwargs):
        for k, v in new_attrs.items():
            self.add_attr(k, v)
        for k, v in kwargs.items():
            self.add_attr(k, v)

    def set_attrs(self, *args, **kwargs):
        for kwarg in kwargs:
            if kwarg in self._data:
                self._data[kwarg] = kwargs[kwarg]

    def get_attr(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"unknown attribute {name}")
    
    def add_render_plugin(self,instance):
        self._renderer_list.append(instance)

    def render(self,*args,**kwargs):
        if not self._renderer_list:
            log.error("Cannot render data as no renderer registred")
        for render_plugin in self._renderer_list:
            render_plugin.render(self)

    def save(self,*args,**kwargs):
        self.render(*args,**kwargs)


class FRUBaseList(UserList):
    def __init__(self, *args, **kwargs):
        self._allowed_class_types = []
        super().__init__()

    def append(self, item) -> None:
        if item.__class__ in self._allowed_class_types:
            item._parent = self
            return self.data.append(item)

        raise ValueError(
            f"Cannot add a {item.__class__.__name__} item to {self.__class__.__name__}. Allowed types are {self._allowed_class_types}"
        )


class FRUBaseDict(UserDict):
    def __init__(self, *args, **kwargs):
        self._allowed_class_types = []
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value) -> None:
        if name in ["_allowed_class_types", "data"] or name.startswith("_"):
            return super().__setattr__(name, value)

        if value.__class__ in self._allowed_class_types:
            self.data[name] = value
            return None
        raise ValueError(
            f"Cannot set a {value.__class__.__name__} item to {self.__class__.__name__}. Allowed types are {self._allowed_class_types}"
        )

    def append(self, obj):
        self.data[obj.name] = obj

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[list(self.data.keys())[key]]
        return super().__getitem__(key)


class Interface(BaseFRU):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            _attrs=["id", "name", "type", "speed", ("capabilities", ())],
            **kwargs,
        )


class InterfaceRange(FRUBaseDict):
    def __init__(self, interface_range, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [Interface]
        self._delimiter = kwargs.get("delimiter", "/")
        self._range_delimiter = kwargs.get("delimiter", "-")
        self._start_name, self._stop_name = interface_range.split(self._range_delimiter)
        tmp = self._start_name.split(self._delimiter)
        self._start = int(tmp[-1])
        self._stop = int(self._stop_name.split(self._delimiter)[-1])
        self._prefix = self._delimiter.join(tmp[:-1])
        for i in range(self._start, self._stop + 1):
            name = self._prefix + self._delimiter + str(i)
            self.append(Interface(*args, name=name, **kwargs))


class PSU(BaseFRU):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, _attrs=["id", "type", "power", ("capabilities", ())], **kwargs
        )


class InterfaceDict(FRUBaseDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [Interface]


class PSUList(FRUBaseList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [PSU]


class InfrastructureDevice(BaseFRU):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._data["powersupplies"] = PSUList()


class NetworkedInfrastructureDevice(InfrastructureDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._data["interfaces"] = InterfaceDict()

class BaseRenderer(object):
    def __init__(self,*args,**kwargs):
        pass
    def render(self,obj):
        print(obj)


switch = NetworkedInfrastructureDevice(name="test")
switch.serial_number = "KLUMP1234"
switch.so_nicht = "oarsch"
switch.add_attr("so_gehts", "hallo")
print(switch)
switch.so_gehts = "hihihi"
switch.add_attrs(
    {"entweder_so_list": ["mit", "defaults"]}, oder_so_geht_auch="str default"
)
print(switch)
switch.entweder_so_list.append("haha")
print(switch.powersupplies)
switch.set_attrs(pid="asdf", vendor="citschgo")
print(switch.get_attr("pid"))
try:
    print(switch.get_attr("gibts ned"))
except AttributeError:
    pass
interface = Interface(name="1/1")
interface2 = Interface(name="1/2")

psu_1 = PSU(power=1000)
psu_2 = PSU(power=1500)

print(interface)
switch.interfaces.append(interface)
switch.interfaces.append(interface2)

switch.powersupplies.append(psu_1)
switch.powersupplies.append(psu_2)
print(switch)
print(switch.interfaces[0])


switch2 = NetworkedInfrastructureDevice(name="test2")
switch2.interfaces = InterfaceRange("e1/1-32", speed=1000)

switch3 = NetworkedInfrastructureDevice(name="test3")
switch3.interfaces = InterfaceRange("ten1/1/1-47", speed=1000)


printer=BaseRenderer()
switch3.add_render_plugin(printer)
switch3.render()