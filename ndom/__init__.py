from collections import UserList, UserDict
import json
from copy import deepcopy
import logging
import os
import xxhash
import yaml
log=logging.getLogger()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class AttributeExistsError(BaseException):
    pass


class AutoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if FRUBaseDict in obj.__class__.__bases__:
            return obj.data
        if FRUBaseList in obj.__class__.__bases__:
            return obj.data
        if BaseFRU in obj.__class__.__bases__:
            return obj.data
        return json.JSONEncoder.default(self, obj)



class BaseFRU(object):

    def __init__(self, *args, **kwargs) -> None:
        self._parent = None
        self._renderer_list=[]
        self.data = {}
        self._attrs = kwargs.get(
            "_attrs",
            [
                "id",
                "name",
                "vendor",
                "pid",
                "serial_number",
                "__type__",
                ("capabilities", ()),
            ],
        )
        for attr in self._attrs:
            if isinstance(attr, tuple):
                if isinstance(attr[1], tuple):
                    list(attr[1])
                self.data[attr[0]] = kwargs.get(attr, deepcopy(attr[1]))
            else:
                self.data[attr] = kwargs.get(attr, None)
        self.data["__type__"] = str(self.__class__.__name__)

    def __repr__(self):
        return json.dumps(self.data, cls=AutoJsonEncoder, indent=2, sort_keys=False)

    def __getattr__(self, name: str):
        if name in self.data:
            return self.data[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value) -> None:
        if name in ["data", "_parent","_renderer_list"]:
            super().__setattr__(name, value)
        # we do not implicitly create attributes by access for now
        elif name in self.data:
            self.data[name] = value
        else:
            super().__setattr__(name, value)

    def add_attr(self, name, default=None):
        if name in self.data:
            raise AttributeExistsError(
                f"cannot add already existing attribute {name} to {self.__class__.__name__}"
            )
        self._attrs.append((name, default))
        self.data[name] = default

    def add_attrs(self, new_attrs={}, **kwargs):
        for k, v in new_attrs.items():
            self.add_attr(k, v)
        for k, v in kwargs.items():
            self.add_attr(k, v)

    def set_attrs(self, *args, **kwargs):
        for kwarg in kwargs:
            if kwarg in self.data:
                self.data[kwarg] = kwargs[kwarg]

    def get_attr(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(f"unknown attribute {name}")
    
    def add_render_plugin(self,instance):
        self._renderer_list.append(instance)

    def render(self,*args,**kwargs):
        results=[]
        if not self._renderer_list:
            log.error("Cannot render data as no renderer registred")
        
        for render_plugin in self._renderer_list:
            results.append((render_plugin,render_plugin.render(self,*args,**kwargs)))
        return results
    
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
            f"Cannot add a {item.__class__.__name__} item to {self.__class__.__name__}. Allowed __type__s are {self._allowed_class_types}"
        )


class FRUBaseDict(UserDict):
    def __init__(self, *args, **kwargs):
        self._allowed_class_types = []
        super().__init__(*args, **kwargs)
        self.data["__type__"]=self.__class__.__name__

    def __setattr__(self, name: str, value) -> None:
        if name in ["_allowed_class_types", "data"] or name.startswith("_"):
            return super().__setattr__(name, value)

        if value.__class__ in self._allowed_class_types:
            self.data[name] = value
            return None
        raise ValueError(
            f"Cannot set a {value.__class__.__name__} item to {self.__class__.__name__}. Allowed __type__s are {self._allowed_class_types}"
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
            _attrs=["id", "name", "__type__", "speed", ("capabilities", ())],
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
            *args, _attrs=["id", "__type__", "power", ("capabilities", ())], **kwargs
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
        self.data["powersupplies"] = PSUList()


class NetworkedInfrastructureDevice(InfrastructureDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data["interfaces"] = InterfaceDict()

class BaseRenderer(object):
    def __init__(self,*args,**kwargs):
        self._obj=None
        self._file_suffix="json"
    
    def render(self,obj,*args,**kwargs):
        self._obj=obj
        print(obj)

    def save(self,*args,**kwargs):
        return self.__save_file__(*args,**kwargs)

    def __save_file__(self,*args,**kwargs):
        dirname=None
        filename=kwargs.get("filename")
        path=kwargs.get("path")
        create_destination_directory=kwargs.get("create_destination_directory",True)
        if os.path.isfile(path) and not kwargs.get("overwrite"):
            log.info("destination path exists, use overwrite=True to overwrite")
            return False
        if os.path.isdir(path):
            dirname=path
        if dirname and not kwargs.get("filename"):
            filename=xxhash.xxh32_hexdigest(self._obj) + f".{self._file_suffix}"
            log.info(f"destination path is a directory, but no filename supplied, generated filename {filename}")
        if not dirname and not filename:
            filename=os.path.basename(path)
            dirname=os.path.dirname(path)
        if dirname and not os.path.isdir(dirname) and create_destination_directory:
            os.makedirs(dirname)
        if dirname:
            final_path=dirname + os.path.sep + filename
        else:
            final_path=filename
        with open(final_path ,"w") as fh:
            fh.write(str(self._obj))

class JSONRenderer(BaseRenderer):
    def render(self,obj,*args,**kwargs):
        self._obj=obj
        path=kwargs.get("json_path")
        if path:
            self.save(*args,path=path,**kwargs)
        return str(self._obj)

class YAMLRenderer(BaseRenderer):
    def render(self,obj,*args,**kwargs):
        self.obj=obj
        path=kwargs.get("path")
        # this is not optimal performance wise, but sufficient for now
        data=json.loads(str(obj))
        self._obj=ymlstr=yaml.dump(data)
        path=kwargs.get("yaml_path")
        if path:
            self.save(*args,path=path,**kwargs)
        return ymlstr

class BaseLoader(object):
    def __init__(self,*args,**kwargs):
        self._obj=None
    
    def load(self,*args,**kwargs):
        return self.__load__(data,**kwargs)

    def __load__(self,*args,**kwargs):
        print("---------------")
        _attrs={}
        data=kwargs.get("data",{})
        obj=None
        obj_type=None
        if isinstance(data,dict):
            obj_type=kwargs.get("data",{}).get("__type__")
            if obj_type=="InterfaceRange":
                obj_type="InterfaceDict"
            obj=globals()[obj_type]()
            for k,v in kwargs.get("data",{}).items():
                # print(k,v)
                if k == "__type__":
                    pass
                elif isinstance(v,list):
                    obj.data[k]=self.__load__(data=v)
                elif isinstance(v,dict):
                    obj.data[k]=self.__load__(data=v)
                else:                    
                    obj.set_attrs(**{k:v})
        elif isinstance(data,list):
            obj=data
        else:
            obj_type=data.__class__.__name__
        return obj
    
        # print(data)
        # if isinstance(data,dict):
        #     obj_type=kwargs.get("data",{}).get("__type__")
        # if obj_type:
        #     obj=globals()[obj_type]()
        # for k,v in kwargs.get("data",{}).items():
        #     if isinstance(v,list):
        #         if obj_type:
        #             obj[k]=self.__load__(data=v)
        #         else:
        #             return []
        #     if isinstance(v,dict):
        #         print(k,v)
        #         if obj_type:
        #             obj[k]=self.__load__(data=v)
        #         else:
        #             return {}
        #     else:
        #         obj.set_attrs(**{k:v})
        # return obj
        # print (obj)
        

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

switch3 = NetworkedInfrastructureDevice(name="test3")
switch3.interfaces = InterfaceRange("ten1/1/1-2")


printer=BaseRenderer()

jsonwriter=JSONRenderer()
yamlwriter=YAMLRenderer()

switch3.add_render_plugin(jsonwriter)
switch3.add_render_plugin(yamlwriter)
# switch3.add_render_plugin(printer)

from pprint import pprint
data=switch3.render(json_path="switch.json",yaml_path="switch.yaml",overwrite=True)

parsed_data=json.loads(data[0][1])
pprint(parsed_data)
test_loader=BaseLoader()
print("result")
print(test_loader.load(data=parsed_data))