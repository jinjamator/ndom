from .base import BaseLoader
import yaml
import os

class YAMLLoader(BaseLoader):
    def __init__(self,*args,**kwargs):
        self._obj=None
    
    def load(self,path,*args,**kwargs):
        if os.path.isfile(path):
            with open(path,"r") as fh:
                data=yaml.load(fh,yaml.SafeLoader)
        else:
            raise ValueError(f"{path} is not a file")
        return self.__load__(data=data,**kwargs)

