from .base import BaseLoader
import json
import os

class JSONLoader(BaseLoader):
    def __init__(self,*args,**kwargs):
        self._obj=None
    
    def load(self,path,*args,**kwargs):
        if os.path.isfile(path):
            with open(path,"r") as fh:
                data=json.load(fh)
        else:
            raise ValueError(f"{path} is not a file")
        return self.__load__(data=data,**kwargs)

