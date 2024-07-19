import yaml
from pathlib import Path

class ConfigHandler:
    def __init__(self, path: str):
        self._name = Path(path).name
        with open(path, encoding='utf-8') as config_file:
            self._data = yaml.load(config_file, Loader=yaml.FullLoader)
    
    def get_name(self) -> str:
        return self._name

    def _recursive_get(self, storage: dict, key: str):
        if storage == None :
            return None
        parts = key.split('.', 1)
        if len(parts) == 2:
            return self._recursive_get(storage.get(parts[0], None), parts[1])
        else:
            try: return storage[key]
            except: return None

    def get(self, key: str):
        return self._recursive_get(self._data, key)