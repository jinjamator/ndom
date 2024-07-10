class BaseLoader(object):
    def __init__(self,*args,**kwargs):
        self._obj=None
    
    def load(self,*args,**kwargs):
        return self.__load__(data,**kwargs)

    def __load__(self,*args,**kwargs):
        _attrs={}
        data=kwargs.get("data",{})
        obj=None
        obj_type=None
        if isinstance(data,dict):
            obj_type=kwargs.get("data",{}).get("__type__")
            if obj_type=="InterfaceRange":
                obj_type="InterfaceDict"
            obj=globals()[obj_type]()
            for k,v in kwargs.get("data",{}).items():
                # print(k,v)
                if k == "__type__":
                    pass
                elif isinstance(v,list):
                    obj.data[k]=self.__load__(data=v)
                elif isinstance(v,dict):
                    obj.data[k]=self.__load__(data=v)
                else:                    
                    obj.set_attrs(**{k:v})
        elif isinstance(data,list):
            obj=data
        else:
            obj_type=data.__class__.__name__
        return obj
    
