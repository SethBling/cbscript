from typing import Literal

import yaml
from pathlib import Path
import fnmatch

config_path = Path(__file__).parent/"config.yml"

class Config:
    optm_level: int = 1
    instance_path: Path | None = None
    world_redirects: dict[str,str] = {}
    glob_redirects:  dict[str,str] = {}

    @classmethod
    def load(cls, error: Literal['silence','print','raise'] = 'raise'):
        if not config_path.exists():
            return
        if error not in ('silence','print','raise'):
            # default to raise
            error = 'raise'
        try:
            data = yaml.safe_load(config_path.open())
        except Exception as ex:
            if error == 'raise':
                raise ex
            if error == 'print':
                print("Could not parse config file!")
                print(type(ex).__name__+':',ex)
                return
            # silence
            return

        cls.optm_level = data.get("optm_level",1)
        instance_path = data.get('instance_path')
        if instance_path is None:
            cls.instance_path = cls.try_guess_instance_path()
        else:
            cls.instance_path = Path(instance_path)

        cls.world_redirects.clear()

        if "world_redirects" in data and data['world_redirects'] is not None:
            try:
                cls.parse_redirects(data["world_redirects"])
            except TypeError as ex:
                if error == 'raise':
                    raise ex
                if error == 'print':
                    print("Could not parse world_redirects!")
                    print(type(ex).__name__+':',ex)
                    return
                # silence
                return
    
    @classmethod
    def parse_redirects(cls, redirects):
        if not isinstance(redirects, dict):
            raise TypeError("redirects can only be a dictionary")

        for key,val in redirects.items():
            if not isinstance(val,str):
                raise TypeError(f"redirect '{key}' has invalid type")
            if any(c in key for c in '[*?'):
                cls.glob_redirects[key] = val
            else:
                cls.world_redirects[key] = val
    
    @classmethod
    def resolve(cls, path: str, prefix = ""):
        if Path(path).is_absolute():
            return Path(path)
        if cls.instance_path is None:
            return config_path.parent / 'out'
        return cls.instance_path / prefix / path

    @classmethod
    def get_world(cls, world: str) -> Path | None:
        if Path(world).is_absolute():
            out = Path(world)
            if not out.exists() and '_' in cls.world_redirects:
                return cls.resolve(cls.world_redirects['_'],'saves')
            return out
        if world in cls.world_redirects:
            return cls.resolve(cls.world_redirects[world], 'saves')
        for k,v in cls.glob_redirects.items():
            if fnmatch.fnmatch(world,k):
                return cls.resolve(v, 'saves')
        out = cls.resolve(world,'saves')
        if not out.exists() and '_' in cls.world_redirects:
            return cls.resolve(cls.world_redirects['_'],'saves')
        return out

    @classmethod
    def try_guess_instance_path(cls) -> Path | None:
        # TODO: use the path of the last used instance by the offical client
        #       IIRC this can be done with loading some json from the .minecraft folder
        return None

# little script to help check the config
if __name__ == "__main__":
    from sys import argv
    Config.load()
    print("Loaded successfully!")
    print("world_redirects:")
    for k,v in Config.world_redirects.items():
        print(f"  {k}: {v}")
    for k,v in Config.glob_redirects.items():
        print(f"  {k}: {v}")
    
    for i in argv[1:]:
        print(i,"->",Config.get_world(i))
