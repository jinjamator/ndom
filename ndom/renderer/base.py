import logging
import os
import xxhash
log=logging.getLogger()

class BaseRenderer(object):
    def __init__(self,*args,**kwargs):
        self._obj=None
        self._file_suffix="json"
    
    def render(self,obj,*args,**kwargs):
        self._obj=obj
        print(obj)

    def save(self,*args,**kwargs):
        return self.__save_file__(*args,**kwargs)

    def __save_file__(self,*args,**kwargs):
        dirname=None
        filename=kwargs.get("filename")
        path=kwargs.get("path")
        create_destination_directory=kwargs.get("create_destination_directory",True)
        if os.path.isfile(path) and not kwargs.get("overwrite"):
            log.info("destination path exists, use overwrite=True to overwrite")
            return False
        if os.path.isdir(path):
            dirname=path
        if dirname and not kwargs.get("filename"):
            filename=xxhash.xxh32_hexdigest(self._obj) + f".{self._file_suffix}"
            log.info(f"destination path is a directory, but no filename supplied, generated filename {filename}")
        if not dirname and not filename:
            filename=os.path.basename(path)
            dirname=os.path.dirname(path)
        if dirname and not os.path.isdir(dirname) and create_destination_directory:
            os.makedirs(dirname)
        if dirname:
            final_path=dirname + os.path.sep + filename
        else:
            final_path=filename
        with open(final_path ,"w") as fh:
            fh.write(str(self._obj))

