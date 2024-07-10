from . import BaseFRU
from . import BaseFRUList

class PSU(BaseFRU):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, _attrs=["id", "__type__", "power", ("capabilities", ())], **kwargs
        )

class PSUList(BaseFRUList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_class_types = [PSU]

