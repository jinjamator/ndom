from .base import BaseRenderer
import json
import yaml

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