class BaseConfiguration(object):
    def __init__(self,cfg=None):
        if cfg:
            self._data=self.__parse__(cfg)
        else:
            self._data=None
        
    
    def __parse__(self,data):
        raise NotImplementedError("no configuration parsing implemented")
    