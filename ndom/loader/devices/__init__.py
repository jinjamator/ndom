import logging
from jinjamator.plugins.content import ssh

import os, re, json
from glob import glob
from ..base import BaseLoader
from datetime import datetime
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class FakeJinjamator(object):
    def __init__(self):
        self.configuration = {}
        pass

    def handle_undefined_var(self, var_name):
        log.debug(f"handle_undefined_var {var_name}")


_jinjamator = FakeJinjamator()
setattr(ssh, "_jinjamator", _jinjamator)


class DeviceLoader(BaseLoader):
    def __init__(self, ip, username, password, platform, **kwargs):
        self._username = username
        self._ip = ip
        self._password = password
        self._platform = platform
        self.__query_cache__ = {}
        self.dom = None
        self._persistent_cache_basedir=kwargs.get("persistent_cache_basedir",False)
        self._persistent_cache_lifetime=kwargs.get("persistent_cache_lifetime",86400)
        self._persistent_cache_dir=None
        if self._persistent_cache_basedir:
            self._persistent_cache_dir=self._persistent_cache_basedir + os.sep + self.get_valid_filename(self._ip)
            self._init_persistent_cache()

    def get_valid_filename(self, name):
        """
        Return the given string converted to a string that can be used for a clean
        filename. Remove leading and trailing spaces; convert other spaces to
        underscores; and remove anything that is not an alphanumeric, dash,
        underscore, or dot.
        >>> get_valid_filename("john's portrait in 2004.jpg")
        'johns_portrait_in_2004.jpg'
        
        this function is taken from django framework

        """
        
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            raise ValueError("Could not derive file name from '%s'" % name)
        return s

    def _init_persistent_cache(self):
        os.makedirs(self._persistent_cache_dir,exist_ok=True)

        if not os.path.isdir(self._persistent_cache_dir):
            raise ValueError(f"persistent_cache_dir {self._persistent_cache_dir} is not a directory")
        for filename in glob(self._persistent_cache_dir + os.sep + "/*.ndomcache"):
            if int(os.path.getmtime(filename)) + int(self._persistent_cache_lifetime) > int(datetime.timestamp(datetime.now())) or self._persistent_cache_lifetime < 0:
                print("use cache")
                with open(filename,"r") as fh:
                    tmp=json.loads(fh.read())
                    self.__query_cache__[tmp["command"]]=tmp["value"]
            else:
                os.remove(filename)

    def _save_to_persistent_cache(self,command,value):
        filename=self.get_valid_filename(command) + ".ndomcache"
        with open(self._persistent_cache_dir + os.sep + filename,"w") as fh:
            fh.write(json.dumps(
                {
                    "command":command,
                    "value":value
                }

            ))


    def query(self, command, **kwargs):
        no_cache=kwargs.get("no_cache",False)
        if command in self.__query_cache__ and no_cache or command not in self.__query_cache__:
            log.debug(f"running {command} ssh on {self._ip}")   
            self.__query_cache__[command]=ssh.query(
                command,
                device_type=self._platform,
                ip=self._ip,
                username=self._username,
                password=self._password,
            )
            if self._persistent_cache_dir:
                self._save_to_persistent_cache(command,self.__query_cache__[command])
        else:
            log.debug(f"returing cached result of {command} on {self._ip}")
        
        return self.__query_cache__[command]


    def __discover__(self):
        raise NotImplementedError("__discover__ not implemented")

    def load(self):
        self.__discover__()
