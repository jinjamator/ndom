from .base import BaseRenderer

class JSONRenderer(BaseRenderer):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._file_suffix=kwargs.get("file_suffix","json")
        

    def render(self,obj,*args,**kwargs):
        self._obj=obj
        if self.destination_path:
            self.save(*args,path=self.destination_path,**kwargs)
        return str(self._obj)
    
