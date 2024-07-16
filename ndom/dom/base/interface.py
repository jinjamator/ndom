from . import BaseFRU,BaseFRUDict
class Interface(BaseFRU):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            _attrs=["id", "name", "__type__", "speed", "status", "admin_status", ("capabilities", ())],
            **kwargs,
        )


class InterfaceRange(BaseFRUDict):
    def __init__(self, interface_range=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if interface_range:
            self.__add__(interface_range,*args,**kwargs)
    
    def __add__(self, data,*args,**kwargs):
        if isinstance(data,str):
            self._allowed_class_types = [Interface]
            self._delimiter = kwargs.get("delimiter", "/")
            self._range_delimiter = kwargs.get("range_delimiter", "-")
            self._start_name, self._stop_name = data.split(self._range_delimiter)
            tmp = self._start_name.split(self._delimiter)
            self._start = int(tmp[-1])
            self._stop = int(self._stop_name.split(self._delimiter)[-1])
            self._prefix = self._delimiter.join(tmp[:-1])
            for i in range(self._start, self._stop + 1):
                name = self._prefix + self._delimiter + str(i)
                self.append(Interface(*args, name=name, **kwargs))
    


class InterfaceDict(BaseFRUDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [Interface]
