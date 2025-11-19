import re, json
from decimal import Decimal
from datetime import datetime

class ListOfDicts(list):
    metadata = {}

    def __init__(self, *args, metadata:dict = {}):
        super().__init__()
        self._active_index = 0
        if not isinstance(metadata, dict): raise TypeError("metadata must be a dict")
        self.metadata = metadata 
        self._syncing = False
        self._synced_keys = set()  # Track keys synced from dict
        
        # Collect all class-level attributes from the entire inheritance chain
        self._class_attrs = set()
        for cls in type(self).__mro__:
            if cls is object:
                continue
            self._class_attrs.update(cls.__dict__.keys())
        
        # Initialize with any provided items
        for item in args:
            if isinstance(item, (list, tuple)):
                for subitem in item:
                    self.append(subitem)
            else:
                self.append(item)
    

    @property
    def active_index(self):
        if len(self)==0: self._active_index = None
        return self._active_index
    @active_index.setter
    def active_index(self, value):
        if not isinstance(value, int):  raise TypeError("active_index must be an integer")
        if value < 0: value = len(self) + value # wrap to the back
        if value < 0 or (len(self) > 0 and value >= len(self)): raise IndexError("active_index out of range")
        self._active_index = value
        self._sync_from_dict()
    

    def append(self, item):
        if not isinstance(item, dict):
            raise TypeError("All elements must be of type dict")
        super().append(item)
        if len(self) == 1:  # First item added
            self._active_index = 0
            self._sync_from_dict()
    

    def insert(self, index, item):
        if not isinstance(item, dict):
            raise TypeError("All elements must be of type dict")
        super().insert(index, item)
        if self._active_index >= index:
            self._active_index += 1
        self._sync_from_dict()
    

    def extend(self, items):
        for item in items:
            if not isinstance(item, dict):
                raise TypeError("All elements must be of type dict")
        super().extend(items)
        self._sync_from_dict()


    def udpate_metadata(self, **kwargs) -> "ListOfDicts":
        """
        Append a list of key/value pairs to the metadata dictionary, and return the instance.
        """
        self.metadata.update(kwargs)
        return self
    

    def make_datatypes_dbsafe(self, inplace:bool = False) -> "ListOfDicts":
        """
        Returns a copy of the ListOfDicts instance with datetime converted to strings and floats converted to Decimal.
        """
        def convert(obj):
            if   isinstance(obj, list):     return [convert(item) for item in obj]
            elif isinstance(obj, dict):     return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, float):    return Decimal(str(obj))
            elif isinstance(obj, datetime): return obj.isoformat()
            else: return obj
        rtn = ListOfDicts(convert(self))
        if inplace: self.clear(); self.extend(rtn); return self
        return rtn
        


    def make_datatypes_pyobj(self, inplace:bool = False) -> "ListOfDicts":
        """
        Returns a copy of the ListOfDicts instance with strings converted to datetime objects and Decimals converted to floats.
        """
        def convert(obj):
            if   isinstance(obj, list):     return [convert(item) for item in obj]
            elif isinstance(obj, dict):     return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, Decimal):  return float(obj)
            elif isinstance(obj, str):
                iso_regex = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?$")
                if iso_regex.match(obj) is None: return obj
                try: return datetime.fromisoformat(obj)
                except ValueError: return obj
            else: return obj
        rtn = ListOfDicts(convert(self))
        if inplace: self.clear(); self.extend(rtn); return self
        return rtn


    def to_json(self) -> str:
        """Convert instance to JSON string"""
        rtn = { 'metadata': self.metadata, 'data': self.make_datatypes_dbsafe() }
        return json.dumps(rtn, default=str, indent=2)


    def from_json(self, json_content: str) -> "ListOfDicts":
        """Load data from JSON string content, including metadata if included. This replaces any existing data."""
        jsondoc = json.loads(json_content)
        self.metadata = {**jsondoc.get('metadata', {})}
        self.clear()
        self.extend(jsondoc.get('data', []))
        self.make_datatypes_pyobj(inplace=True)
        return self


    def addkey_if_missing(self, keys:list, value_if_missing=None) -> "ListOfDicts":
        """
        Add keys to all dicts in the list if it's missing.
        """
        if isinstance(keys, str): keys = [keys]
        for key in keys:
            for d in self:
                if key not in d: d[key] = value_if_missing
        return self


    def _sync_from_dict(self):
        if self._syncing:
            return
        
        self._syncing = True
        try:
            # Remove old synced properties (only those that were synced from dict)
            for key in list(self._synced_keys):
                if hasattr(self, key):
                    delattr(self, key)
            self._synced_keys.clear()
            
            # Add new properties from active dict (only if list is not empty)
            if len(self) > 0:
                if self._active_index == None: self._active_index = 0
                active_dict = self[self._active_index]
                for key, value in active_dict.items():
                    object.__setattr__(self, key, value)
                    self._synced_keys.add(key)
        finally:
            self._syncing = False
    

    def _sync_to_dict(self, key, value):
        if self._syncing or len(self) == 0:
            return
        
        # Don't sync class-level attributes to the dict
        if key in self._class_attrs:
            return
        
        self._syncing = True
        try:
            self[self._active_index][key] = value
        finally:
            self._syncing = False
    

    def __setitem__(self, index, item):
        if not isinstance(item, dict):
            raise TypeError("All elements must be of type dict")
        super().__setitem__(index, item)
        if index == self._active_index:
            self._sync_from_dict()
            

    def __delitem__(self, index):
        super().__delitem__(index)
        if index < self._active_index:
            self._active_index -= 1
        elif index == self._active_index:
            self._sync_from_dict()
    

    def clear(self):
        super().clear()
        self._active_index = None
        self._sync_from_dict()
    

    def pop(self, index=-1):
        result = super().pop(index)
        if len(self) == 0:
            self._active_index = None
        elif index == self._active_index or (index == -1 and self._active_index == len(self)):
            if self._active_index >= len(self):
                self._active_index = len(self) - 1 if len(self) > 0 else None
        self._sync_from_dict()
        return result


    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'active_index':
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
            if hasattr(self, '_syncing') and not self._syncing and len(self) > 0:
                self._sync_to_dict(name, value)
    

    def __getattribute__(self, name):
        # For non-special attributes, ensure sync
        if not name.startswith('_') and name != 'active_index' and hasattr(self, '_active_index'):
            try:
                if len(self) > 0 and name in self[self._active_index]:
                    return self[self._active_index][name]
            except (IndexError, KeyError):
                pass
        return super().__getattribute__(name)


    def __str__(self):
        return f"ListOfDicts(\n{self.to_json()}\n)"



