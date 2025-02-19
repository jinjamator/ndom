from . import BaseFRU, BaseFRUDict
from . exceptions import AttributeExistsError

class Interface(BaseFRU):
    def __init__(self, *args, **kwargs):
        _attrs=kwargs.get("_attrs",["id", "name", "__type__", "speed", "status", "admin_status", ("capabilities", ())])
        try:
            del kwargs["_attrs"]
        except:
            pass
        super().__init__(
            *args,
            _attrs=_attrs,
            **kwargs,
        )

class BreakoutInterface(Interface):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            _attrs=["id", "parent" ,"name", "__type__", "speed", "status", "admin_status", ("capabilities", ())],
            _required_attrs=["name", "parent"],
            **kwargs,
        )
        if not isinstance(kwargs["parent"],Interface):
            raise ValueError("parent must be an instance of Interface")
        self._parent_interface=kwargs["parent"]
        
        try:
            self._parent_interface.add_attr("breakout_interfaces",InterfaceRange())
        except AttributeExistsError:
            pass
        self._parent_interface.breakout_interfaces.append(self)


        
        

class InterfaceRange(BaseFRUDict):
    def __init__(self, interface_range=None, *args, **kwargs):
        super().__init__()
        if interface_range:
            self.__add__(interface_range,*args,**kwargs)
    
    def append(self, obj,*args,**kwargs):
        if isinstance(obj,InterfaceRange):
            self.__add__(obj,*args,**kwargs)
        elif isinstance(obj,str):
            self.__add__(obj,*args,**kwargs)
        else:
            return super().append(obj)
    
    def __add__(self, data,*args,**kwargs):
        self._allowed_class_types = [Interface]
        self._delimiter = kwargs.get("delimiter", "/")
        self._range_delimiter = kwargs.get("range_delimiter", "-")
        if isinstance(data,InterfaceRange):
            for k,v in data.items():
                if k not in self.data:
                    self.data[k]=v
                else:
                    if k not in ["__type__"]:
                        raise ValueError(f"interface {k} already definded")
                    
        if isinstance(data,str):
            if self._range_delimiter in data:
                self._start_name, self._stop_name = data.split(self._range_delimiter)            
                tmp = self._start_name.split(self._delimiter)
                self._start = int(tmp[-1])
                self._stop = int(self._stop_name.split(self._delimiter)[-1])
                self._prefix = self._delimiter.join(tmp[:-1])
                for i in range(self._start, self._stop + 1):
                    name = self._prefix + self._delimiter + str(i)
                    self.append(Interface(*args, name=name, **kwargs))
            else:
                self.append(Interface(*args, name=data, **kwargs))
        if isinstance(data,Interface):
            self.append(data)
        return self
    


class InterfaceDict(BaseFRUDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [Interface]
