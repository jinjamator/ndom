from .base import BaseRenderer
import json
import yaml

class YAMLRenderer(BaseRenderer):

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._file_suffix=kwargs.get("file_suffix","yml")

    def render(self,obj,*args,**kwargs):
        self.obj=obj
        # this is not optimal performance wise, but sufficient for now
        data=json.loads(str(obj))
        self._obj=ymlstr=yaml.dump(data)
        if self.destination_path:
            self.save(*args,path=self.destination_path,**kwargs)
        return ymlstr