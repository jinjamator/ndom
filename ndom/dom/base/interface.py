from . import BaseFRU,BaseFRUDict
class Interface(BaseFRU):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            _attrs=["id", "name", "__type__", "speed", ("capabilities", ())],
            **kwargs,
        )


class InterfaceRange(BaseFRUDict):
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
        


class InterfaceDict(BaseFRUDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [Interface]
