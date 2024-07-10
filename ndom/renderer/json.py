from .base import BaseRenderer

class JSONRenderer(BaseRenderer):
    def render(self,obj,*args,**kwargs):
        self._obj=obj
        path=kwargs.get("json_path")
        if path:
            self.save(*args,path=path,**kwargs)
        return str(self._obj)
    
