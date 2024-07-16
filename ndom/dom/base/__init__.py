from collections import UserList, UserDict
from copy import deepcopy
import json
from .exceptions import AttributeExistsError,MissingRequiredInstanceAttribute,RendererAlreadyRegistredError
import logging
log=logging.getLogger(__file__)

class AutoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if BaseFRUDict in obj.__class__.__bases__:
            return obj.data
        if BaseFRUList in obj.__class__.__bases__:
            return obj.data
        if BaseFRU in obj.__class__.__bases__:
            return obj.data
        return json.JSONEncoder.default(self, obj)
    

class BaseFRU(object):

    def __init__(self, *args, **kwargs) -> None:
        self._parent = None
        self._renderer={}
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
        self._required_attrs=kwargs.get("_required_attrs",[
            "name"
        ])
        for attr in self._attrs:
            if isinstance(attr, tuple):
                if isinstance(attr[1], tuple):
                    list(attr[1])
                self.data[attr[0]] = kwargs.get(attr, deepcopy(attr[1]))
            else:
                self.data[attr] = kwargs.get(attr, None)
            if attr in self._required_attrs and not self.data[attr]:
                  raise MissingRequiredInstanceAttribute(f"{attr} missing in kwargs, you have to supply at least {self._required_attrs}")

        self.data["__type__"] = str(self.__class__.__name__)
        
              

    def __repr__(self):
        return json.dumps(self.data, cls=AutoJsonEncoder, indent=2, sort_keys=False)

    def __getattr__(self, name: str):
        if name in self.data:
            return self.data[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value) -> None:
        if name in ["data", "_parent","_renderer"]:
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
    
    def add_render_plugin(self,name,instance):
        if name in self._renderer:
            raise RendererAlreadyRegistredError(f"renderer with name {name} already registred")
        print (self._renderer)
        self._renderer[name]=instance

    def render(self,name,*args,**kwargs):
        if name not in self._renderer:
            log.error(f"cannot find renderer {name}, registred render plugins : {self._renderer}")
        return self._renderer[name].render(self,*args,**kwargs)
    
    def render_all(self,*args,**kwargs):
        results=[]
        for render_plugin_name,render_plugin in self._renderer.items():
            results.append((render_plugin_name,render_plugin.render(self,*args,**kwargs)))
        return results   

    def save(self,*args,**kwargs):
        self.render(*args,**kwargs)


class BaseFRUList(UserList):
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


class BaseFRUDict(UserDict):
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
    
    def remove(self, obj):
        if isinstance(obj,str):

            del self.data[obj]
        else:
            del self.data[obj.name]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[list(self.data.keys())[key]]
        return super().__getitem__(key)
