import copy, json, datetime
from typing import List, Dict, Any, Iterable, Optional, Type
from enum import StrEnum
from pydantic_core import core_schema
from typing import Any




class ImmutableDict(Dict):
    """An immutable dict subclass, which removes all ability to update the dict directly."""
    def __setitem__(self, key, value): raise AttributeError("Cannot modify items in an immutable dictionary")
    def __delitem__(self, key): raise AttributeError("Cannot delete items from an immutable dictionary")
    def update(self, *args, **kwargs): raise AttributeError("Cannot update an immutable dictionary")        
    def clear(self): raise AttributeError("Cannot clear an immutable dictionary")
    def pop(self, *args, **kwargs): raise AttributeError("Cannot pop from an immutable dictionary")
    def popitem(self):raise AttributeError("Cannot popitem from an immutable dictionary")


class listofdicts(List[Dict[str, Any]]):
    """
    listofdicts: Strongly typed list of dictionaries with optional immutability, schema validation, 
    runtime strict type enforcement, safe mutation, extra-iterable metadata support, and full JSON serialization.
    """

    def __init__(
        self,
        iterable: Optional[Iterable[Dict[str, Any]]] = None,
        *,
        schema: Optional[Dict[str, Type]] = None,
        schema_add_missing: bool = False,
        schema_constrain_to_existing: bool = False,
        immutable: bool = False,
        append_only: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):

        self.immutable = immutable
        self.append_only = append_only
        self._schm = schema
        self._schmaddmiss = schema_add_missing
        self._shmcnst2xst = schema_constrain_to_existing
        self._metadata = metadata if metadata else {}

        if iterable is None:
            super().__init__()
        else:
            iterable = self.validate_all(list(iterable))
            super().__init__(iterable)


    @property
    def metadata(self):
        """
        Metadata is a dictionary of arbitrary key-value pairs to be stored with the listofdicts instance.
        This is intended to store information about the listofdicts instance that is not part of the core data.
        This is not exposed during object iteration or enumeration, but can be optionally serialized to JSON.
        """
        if self._metadata is None: self._metadata = {}
        return self._metadata

    @metadata.setter
    def metadata(self, value:dict):
        if type(value) != dict and value is not None: raise TypeError("Metadata must be a dict.")
        self._metadata = value

    @property
    def schema(self):
        """
        Schema is a dictionary of key-type pairs that specifies the {KeyName: Type} of each key in the listofdicts,
        for example: {"key1": str, "key2": int, "key3": float}.
        This is used for runtime type enforcement and schema validation, using the two flag options:
        - schema_constrain_to_existing - all data keys must exist in the schema.
        - schema_add_missing - any data keys missing compared to the schema will be added with a value of None.
        """
        return self._schm

    @schema.setter
    def schema(self, value:dict):
        if type(value) != dict and value is not None: raise TypeError("Schema must be a dict.")
        old_value = self._schm
        self._schm = value
        try:
            self.validate_all(self)
        except TypeError:
            self._schm = old_value
            raise TypeError("Schema validation failed - make sure current data adheres to new schema.")
        return self._schm

    @property
    def schema_constrain_to_existing(self) -> bool:
        """
        If set to True with a defined schema, all keys in the dictionary data must also be present in the schema.
        This constrains data added to the listofdicts to only keys defined in the schema (if defined).
        Note, this does NOT REQUIRE all keys in the schema to be present in the dictionary data, it only enforces the constraint.
        To add missing keys when adding new listofdict elements, set schema_add_missing to True.
        """
        return self._shmcnst2xst
    
    @schema_constrain_to_existing.setter
    def schema_constrain_to_existing(self, value:bool):
        if type(value) != bool: raise TypeError("schema_constrain_to_existing must be a bool.")
        
        # if schema is False, or value is False, no validation needed
        if not self.schema or not value: self._shmcnst2xst = value 
        else: # only validate if schema is set, AND value is True
            old_value = bool(self._shmcnst2xst)
            self._shmcnst2xst = value
            try:
                self.validate_all(self) 
            except TypeError:
                self._shmcnst2xst = old_value # revert
                raise TypeError("Schema validation failed - make sure current data adheres to new schema requirements.")
        return self._shmcnst2xst


    @property
    def schema_add_missing(self) -> bool:
        """
        If set to True with a defined schema, any keys in the schema that are not present in the dictionary data will be added with a value of None.
        This is useful when adding new listofdicts elements, to ensure that all keys in the schema are present in the dictionary data.
        Note, this does NOT CONSTRAIN data keys to only keys defined in the schema, it only adds missing keys.
        To constrain data to only keys defined in the schema, set schema_constrain_to_existing to True.
        """
        return self._schmaddmiss
    
    @schema_add_missing.setter
    def schema_add_missing(self, value:bool):
        if type(value) != bool: raise TypeError("schema_add_missing must be a bool.")
        
        self._schmaddmiss = value
        if self.schema and value: # if schema is set, AND add missing = True, add missing keys
            for d in self:
                missing_keys = [k for k in list(self.schema.keys()) if k not in list(d.keys())] 
                for k in missing_keys: d[k] = None
        return self._schmaddmiss
        

    def append(self, item: Dict[str, Any]) -> None:
        """
        Append a dictionary to the end of this listofdicts object. 
        This will fail if the object has been made immutable (append_only is fine), or
        if the schema was defined and enforced, and the new dictionary keys do not match the schema.
        """
        self._check_mutable(appending=True)
        item = self.validate_item(item)
        super().append(item)

    def extend(self, other: 'listofdicts') -> None:
        """
        Extend THIS listofdicts object (in place) with dictionaries from another listofdicts object (returning None).
        This will fail if this object has been made immutable (append_only is fine), or
        if the schema was defined and enforced, and the new dictionary keys do not match the schema.
        """
        self._check_mutable(appending=True)
        other = self.validate_all(other)
        super().extend(other)
        return self

    def __add__(self, other: 'listofdicts') -> 'listofdicts':
        self.extend(other)
        return self
    
    def __iadd__(self, other):        
        if isinstance(other, listofdicts): 
            self.extend(other)
            return self
        if isinstance(other, dict): 
            self.append(other)
            return self
        raise TypeError("Only listofdicts or dict instances can be added with +=.")
     
    def __setitem__(self, index, value):
        self._check_mutable(appending=False)
        if isinstance(index, slice):
            value = self.validate_all(copy.deepcopy(value))
            super().__setitem__(index, value)
        else:
            value = self.validate_item(copy.deepcopy(value))
            super().__setitem__(index, value)

    def __delitem__(self, index):
        self._check_mutable(appending=False)
        super().__delitem__(index)

    def __str__(self):
        max_key_len = max([len(k) for k in self.unique_keys()])       
        rtn = []
        for r in self:
            rtn.append('{\n\t' + '\n\t'.join([f'{str(n).ljust(max_key_len)} : {v}' for n,v in r.items()]) + '\n}') 
        return  '[' + ','.join(rtn) + ']\nMetadata:\n' + str(self.metadata)
 
    @classmethod # for pydantic support
    def __get_pydantic_core_schema__(
        cls, 
        source_type: Any, 
        handler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.list_schema(core_schema.dict_schema())
        )
    
    @classmethod  # for pydantic support
    def _validate(cls, value):
        # Convert value into a listofdicts instance
        if isinstance(value, cls): return value
        if isinstance(value, dict): return cls([value])   
        return cls(value)


    def _check_mutable(self, appending:bool = False):
        if self.immutable: raise AttributeError("This listofdicts instance is immutable.")
        if self.append_only and not appending: raise AttributeError("This listofdicts instance is append only, you cannot modify existing entries.")

    def validate_all(self, iterable: Iterable[Dict[str, Any]] = None) -> list:
        """
        Validate all elements in the listofdicts object.
        This will fail if the schema was defined and enforced, and any dictionary keys do not match the schema.
        This can be useful to ensure that all elements in the listofdicts object are valid, before applying a new schema.
        """
        if iterable is None: iterable = self
        if not isinstance(iterable, list): raise TypeError("Requires a list or listofdicts type.")
        for pos, item in enumerate(iterable): 
            iterable[pos] = self.validate_item(item) # this does all checking / reporting
        return iterable

    def make_dict_immutable(self, dict_item:dict):
        """
        Subclasses dict with ImmutableDict() object, making it immutable.  This is used automatically when 
        setting the parent to either immutable or append_only, however you can use it on individual dicts 
        while inserting, allowing you have a mixture of mutable and immutable data.  

        Accepts a dict, and returns an ImmutableDict() with update functions disabled.
        """
        return ImmutableDict(dict_item) 
    

    def validate_item(self, new_item: Dict[str, Any]) -> dict:
        """
        Validate a single dictionary element in the listofdicts object.
        This will fail if the schema was defined and enforced, and any dictionary keys do not match the schema.
        This can be useful to ensure the new dict elements is valid, before inserting into the listofdicts object.
        """
        if not isinstance(new_item, dict): raise TypeError("Element must be a dictionary.")
        
        # new_item should be ImmutableDict if the list is immutable or append_only, otherwise just a dict
        if (self.append_only or self.immutable) and type(new_item) != ImmutableDict:  
            new_item = self.make_dict_immutable(new_item)        

        # everything else is schema validation:
        if not self.schema: return new_item

        # deal with extra keys
        if self.schema_constrain_to_existing:
            extra_keys = [k for k in list(new_item.keys()) if k not in  list(self.schema.keys())]
            if extra_keys != []:
                raise TypeError(f"New dictionary has extra keys ({', '.join(extra_keys)}) and schema_constrain_to_existing is True.")

        # deal with missing keys
        missing_keys = [k for k in list(self.schema.keys()) if k not in list(new_item.keys())] 
        if missing_keys != []:
            if self.schema_add_missing: 
                for k in missing_keys: new_item[k] = None
            else: 
                raise TypeError(f"New dictionary has missing keys ({', '.join(missing_keys)}).")

        # check value types: TODO: need to iterate thru schema keys, not new_item keys
        mismatched_types = [f'key "{k}" should be {str(self.schema[k])}, got {str(type(new_item[k]))}' 
                            for k in self.schema.keys() 
                            if (not isinstance(new_item[k], self.schema[k])) and not (new_item[k] is None and self.schema_add_missing)] 
        if mismatched_types != []:
            raise TypeError("New dictionary has mismatched types:\n  " + '\n  '.join(mismatched_types))
        else: 
            pass 
        
        return new_item


    def clear(self):
        """
        Clear the listofdicts object (in place).
        This will fail if this object has been made immutable or append_only.
        """
        self._check_mutable(appending=False)
        super().clear()

    def pop(self, index=-1):
        """
        Remove and return an element from the listofdicts object, at the given index (default last).
        This will fail if this object has been made immutable or append_only.
        """
        self._check_mutable(appending=False)
        return super().pop(index)

    def popitem(self):
        """
        Remove and return an element from the listofdicts object.
        This will fail if this object has been made immutable or append_only.
        """
        self._check_mutable(appending=False)
        return super().popitem()
    
    def remove(self, value):
        """
        Remove an element from the listofdicts object (in place), by value (aka dictionary).
        This will fail if this object has been made immutable or append_only.
        """
        self._check_mutable(appending=False)
        return super().remove(value)
        

    def sort(self, key=None, reverse=False):
        """
        Sort the order of dictionaries within the list by a given dictionary key, with the requirement that 
        the key must be present in all dictionaries in the list.
        This does not effect the data, only it's order within the list, 
        and therefore can be called on immutable listofdicts objects.
        """
        if not all(key in d for d in self): raise TypeError(f"All dicts must contain the sort key: {key}")
        super().sort(key=lambda x: x[key], reverse=reverse)        
        return self

    def unique_keys(self) -> list:
        """
        Returns a list of all unique keys found in all dicts.
        """
        return list(set([k for d in self for k in d.keys()]))
    
    def unique_key_values(self, key:str) -> list:
        """
        Returns a list of all unique values across all dicts in the listofdicts, for a given key.
        """
        if key not in self.unique_keys(): return []
        return list(set([d[key] for d in self if key in d]))
        
    def unique_key_value_len(self, key:str) -> int:
        """
        Returns the character length of each unique value across all dicts in the listofdicts, for a given key.
        """
        values = self.unique_key_values(key)
        return [len(str(v)) for v in values]
    
    def filter(self, filter_key:str, filter_value = None):
        """
        Returns a new listofdicts object, which is a subset of this object, 
        filtered by given a key and value which is applied to the dicts.

        Args:
            filter_key (str): The key in the dict to filter by (required).
            filter_value (Any, optional): The value to filter by. If None (default), returns all dicts that have the filter_key.
        """
        return listofdicts([d for d in self if filter_value == None or d[filter_key] == filter_value ]).copy()

    def copy(self, *, 
             schema: Optional[Dict[str, Type]] = None, 
             schema_add_missing: Optional[bool] = None, 
             schema_constrain_to_existing: Optional[bool] = None, 
             immutable: Optional[bool] = None,
             append_only: Optional[bool] = None) -> 'listofdicts':
        """
        Performs a deep copy of the listofdicts instance, with optional schema and immutability overrides.
        """
        lod = [dict(d) for d in self]
        return listofdicts(copy.deepcopy(lod),
                           schema=schema if schema is not None else self.schema, 
                           schema_add_missing=schema_add_missing if schema_add_missing is not None else self.schema_add_missing, 
                           schema_constrain_to_existing=schema_constrain_to_existing if schema_constrain_to_existing is not None else self.schema_constrain_to_existing,
                           immutable=immutable if immutable is not None else self.immutable,
                           append_only=append_only if append_only is not None else self.append_only
                           )

    def as_mutable(self) -> 'listofdicts':
        """
        Returns a mutable (not immutable nor append_only) deepcopy of this listofdicts instance.
        """
        return self.copy(immutable=False, append_only=False)

    def as_immutable(self) -> 'listofdicts':
        """
        Returns an immutable deepcopy of this listofdicts instance.
        """
        return self.copy(immutable=True)

    def as_append_only(self) -> 'listofdicts':
        """
        Returns an append_only deepcopy of this listofdicts instance.
        """
        return self.copy(append_only=True)

    def update_item(self, index: int, updates: Dict[str, Any]):
        """
        Updates the dictionary object of the list at the given index.  
        This will fail if this object has been made immutable or append_only.

        Args:
            index (int): The index of the dictionary object to update.
            updates (Dict[str, Any]): The dictionary containing the updates to apply.
        """
        self._check_mutable(appending=False)
        if not isinstance(updates, dict): raise TypeError("Updates must be a dict.")
        original = copy.deepcopy(self[index])
        original.update(updates)
        original = self.validate_item(original)
        super().__setitem__(index, original)

    def __repr__(self):
        return f"listofdicts( immutable={self.immutable}, append_only={self.append_only}, schema={self.schema}, \n{list(self)})"

    def __eq__(self, other):
        if not isinstance(other, listofdicts):
            return False
        return list(self) == list(other) and self.immutable == other.immutable and self.schema == other.schema

    def __hash__(self):
        if not self.immutable:
            raise TypeError("Unhashable type: 'listofdicts' (only immutable allowed)")
        return hash((
            tuple(frozenset(item.items()) for item in self),
            frozenset(self.schema.items()) if self.schema else None
        ))



    def to_json(self, *, indent: Optional[int] = None, preserve_metadata: bool = False) -> str:
        """
        Returns a JSON string representation of the listofdicts instance.
        If preserve_metadata is True, all metadata and other settings will be nested under a "metadata" key, 
        and the core iterator data will be nested under a "data" key.
        If preserve_metadata is False, only the core iterator data will be returned, as a list of dictionaries, unnested.         
        """
        if preserve_metadata:
            adj_schema = {n:str(v).split("'")[1] for n,v in self.schema.items()}
            settings = {
                "schema": adj_schema,
                "schema_add_missing": self.schema_add_missing,
                "schema_constrain_to_existing": self.schema_constrain_to_existing,
                "immutable": self.immutable,
                "append_only": self.append_only
            }
            return json.dumps({"metadata": self.metadata, "data": list(self), "settings": settings}, indent=indent)

        return json.dumps(list(self), indent=indent)

    @classmethod
    def from_json(cls, json_str: str, *, 
                  metadata: Optional[Dict[str, Any]] = None, 
                  schema: Optional[Dict[str, Type]] = None, 
                  schema_add_missing: bool = False, 
                  schema_constrain_to_existing: bool = False, 
                  immutable: bool = False, 
                  append_only: bool = False) -> 'listofdicts':
        """
        Creates a listofdicts instance from a JSON string.
        """
        if type(json_str) in(list,dict): json_str = json.dumps(json_str)
        data = json.loads(json_str)
        if isinstance(data, list): # no metadata, just data
            return cls(data, metadata=metadata, immutable=immutable, append_only=append_only, schema=schema, schema_add_missing=schema_add_missing, schema_constrain_to_existing=schema_constrain_to_existing)
        
        # well-formed "data" element is required:
        if not ( isinstance(data, dict) and 
                 "data" in data and 
                 isinstance(data["data"], list)
                ):
            raise ValueError("JSON must represent a list of dicts [{},{},...], or a dictionary with {'metadata': {...}, 'data': [{},{},...], and optional 'settings': {...} } keys.") 
    
        # the rest is optional:
        if 'metadata' not in data: data['metadata'] = {}  # metadata is optional
        if 'settings' not in data: data['settings'] = {}  # settings are optional

        # if schema included, convert schema values (as strings) back into native python types
        if 'schema' in data['settings'] and isinstance(data['settings']['schema'], dict): 
            for sname, svalue in data['settings']['schema'].items(): 
                match svalue.strip(): # safer than eval, which can execute arbitrary code
                    case "str": data['settings']['schema'][sname] = str
                    case "int": data['settings']['schema'][sname] = int
                    case "float": data['settings']['schema'][sname] = float
                    case "bool": data['settings']['schema'][sname] = bool
                    case "date": data['settings']['schema'][sname] = datetime.date
                    case "datetime": data['settings']['schema'][sname] = datetime.datetime
                    case "timedelta": data['settings']['schema'][sname] = datetime.timedelta
                    case "time": data['settings']['schema'][sname] = datetime.time
                    case "list": data['settings']['schema'][sname] = list
                    case "dict": data['settings']['schema'][sname] = dict
                    case "set": data['settings']['schema'][sname] = set
                    case "tuple": data['settings']['schema'][sname] = tuple
                    case "bytearray": data['settings']['schema'][sname] = bytearray
                    case "bytes": data['settings']['schema'][sname] = bytes
                    case "range": data['settings']['schema'][sname] = range
                    case "listofdicts": data['settings']['schema'][sname] = listofdicts
                    case _: data['settings']['schema'][sname] = object
        
        return cls(data["data"], 
                    metadata=data["metadata"],
                    immutable=data["settings"].get("immutable", immutable), 
                    append_only=data["settings"].get("append_only", append_only), 
                    schema=data['settings'].get('schema', schema),
                    schema_add_missing=data['settings'].get('schema_add_missing', schema_add_missing),
                    schema_constrain_to_existing=data['settings'].get('schema_constrain_to_existing', schema_constrain_to_existing)
        )
 

    @classmethod
    def as_llm_prompt(cls, system_prompts, user_prompts, schema:dict = {'role': str, 'content': str}, *prompt_modes ) -> 'listofdicts':
        """
        Creates a listofdicts instance, customized for LLM prompts.
        """
        if type(system_prompts)==str: system_prompts=[system_prompts]
        if type(user_prompts)==str: user_prompts=[user_prompts]
        newobj = cls(immutable=False, append_only=False, schema=schema, schema_add_missing=True, schema_constrain_to_existing=False)

        for prompt_mode in prompt_modes: 
            if prompt_mode not in PROMPT_MODES: raise ValueError(f"Invalid prompt mode: {prompt_mode}\nMust be one of {PROMPT_MODES}")
            newobj.append({'role': 'system', 'content': prompt_mode})
            
        for prompt in system_prompts: newobj.append({'role': 'system', 'content': prompt})  
        for prompt in user_prompts: newobj.append({'role': 'user', 'content': prompt})
        
        return newobj



class PROMPT_MODES(StrEnum):
    ABSOLUTE = "Eliminate all emojis, filler words, hype phrases, soft asks, conversational transitions, and any call-to-action appendixes. Be cold, direct, and factual."
    DEVELOPER = "Think like a senior-level engineer. Prioritize clarity, precision, and code snippets where appropriate. Do not speculate or sugar-coat. Avoid humanlike banter."
    SOCRATIC = "Encourage critical thinking. If a topic lends itself to analysis, respond with a question that challenges assumptions or invites deeper reflection."
    PROFESSOR = "Teach the topic thoroughly. Include definitions, context, key principles, and real-world analogies. Use layered explanations for advanced topics."
    SUMMARIZER = "When text is long, distill it into bullet points, key takeaways, or a concise TL;DR at the top."
    EXPLAINER = "Make complex concepts accessible. Use plain language, visual analogies, and 'explain it to a 5th grader' level when needed."
    DEVILS_ADVOCATE = "Present a reasoned counterargument to dominant assumptions or conventional wisdom, but label it clearly as a hypothetical or challenge."
    LAYMAN = "When technical terms are used, define them in simple English. Avoid jargon unless absolutely necessary."
    LEGAL_SCIENTIFIC = "Use accurate, verifiable information. When citing facts, include references where possible (e.g., 'According to CDC 2022…'). Avoid speculation."
    GPT_AS_TOOL = "Prefer structured outputs: code blocks, tables, checklists, decision trees, or schema. Focus on utility over personality."
    JOURNALIST = "Maintain neutrality. Prioritize facts, clarity, and conciseness. Use inverted pyramid structure: key points first, details later."
    CREATIVE_WRITER = "Where appropriate, weave metaphor, emotion, or narrative structure into the response to enhance engagement."

 

if __name__ == "__main__":

    # from_json (preserve_metadata=True)
    schema = {'dog': str}
    data = [{"dog": "sunny", "legs": 4}, {"dog": "luna", "legs": 4}, {"dog": "stumpy", "legs": 3}, {"dog": "fido"}]
    metadata = {'key1':1, 'key2':2}
    lod = listofdicts.from_json(data, metadata=metadata, schema=schema)

    print(lod) 

    
 
    pass