from typing import List, Dict, Any, Iterable, Optional, Type
from enum import StrEnum
import copy, json

class listofdicts(List[Dict[str, Any]]):
    """
    listofdicts: Strongly typed list of dictionaries with optional immutability, schema validation,
    runtime strict type enforcement, safe mutation, and full JSON serialization support.
    """

    def __init__(
        self,
        iterable: Optional[Iterable[Dict[str, Any]]] = None,
        *,
        schema: Optional[Dict[str, Type]] = None,
        schema_add_missing: bool = False,
        schema_constrain_to_existing: bool = False,
        immutable: bool = False
    ):

        self.immutable = immutable
        self._schm = schema
        self._schmaddmiss = schema_add_missing
        self._shmcnst2xst = schema_constrain_to_existing

        if iterable is None:
            super().__init__()
        else:
            iterable = list(iterable)
            self.validate_all(iterable)
            super().__init__(iterable)


    @property
    def schema(self):
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
        self._check_mutable()
        self.validate_item(item)
        super().append(item)

    def extend(self, other: 'listofdicts') -> None:
        self._check_mutable()
        self.validate_all(other)
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
        self._check_mutable()
        if isinstance(index, slice):
            self.validate_all(value)
            super().__setitem__(index, copy.deepcopy(value))
        else:
            self.validate_item(value)
            super().__setitem__(index, copy.deepcopy(value))

    def __delitem__(self, index):
        self._check_mutable()
        super().__delitem__(index)

    def _check_mutable(self):
        if self.immutable: raise TypeError("This listofdicts instance is immutable.")

    def validate_all(self, iterable: Iterable[Dict[str, Any]] = None):
        if iterable is None: iterable = self
        if not isinstance(iterable, list): raise TypeError("Requires a list or listofdicts type.")
        if not all(isinstance(item, dict) for item in iterable): raise TypeError("All elements must be dicts.")
        for item in iterable: self.validate_item(item)

    def validate_item(self, new_item: Dict[str, Any]):
        if not isinstance(new_item, dict): raise TypeError("Element must be a dictionary.")
        if not self.schema: return

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

    def clear(self):
        self._check_mutable()
        super().clear()

    def pop(self, index=-1):
        self._check_mutable()
        return super().pop(index)

    def popitem(self):
        self._check_mutable()
        return super().popitem()
    
    def remove(self, value):
        self._check_mutable()
        return super().remove(value)
        

    def sort(self, key=None, reverse=False):
        if not all(key in d for d in self): raise TypeError(f"All dicts must contain the sort key: {key}")
        super().sort(key=lambda x: x[key], reverse=reverse)        
        return self

    def unique_keys(self) -> list:
        return list(set([k for d in self for k in d.keys()]))
    
    def unique_key_values(self, key:str) -> list:
        return list(set([d[key] for d in self]))
        

    def copy(self, *, 
             schema: Optional[Dict[str, Type]] = None, 
             schema_add_missing: Optional[bool] = None, 
             schema_constrain_to_existing: Optional[bool] = None, 
             immutable: Optional[bool] = None) -> 'listofdicts':
        return listofdicts(copy.deepcopy(self),
                           schema=schema if schema is not None else self.schema, 
                           schema_add_missing=schema_add_missing if schema_add_missing is not None else self.schema_add_missing, 
                           schema_constrain_to_existing=schema_constrain_to_existing if schema_constrain_to_existing is not None else self.schema_constrain_to_existing,
                           immutable=immutable if immutable is not None else self.immutable)

    def as_mutable(self) -> 'listofdicts':
        return self.copy(immutable=False)

    def as_immutable(self) -> 'listofdicts':
        return self.copy(immutable=True)

    def update_item(self, index: int, updates: Dict[str, Any]):
        self._check_mutable()
        if not isinstance(updates, dict):
            raise TypeError("Updates must be a dict.")
        original = copy.deepcopy(self[index])
        original.update(updates)
        self.validate_item(original)
        super().__setitem__(index, original)

    def __repr__(self):
        return f"listofdicts({list(self)}, immutable={self.immutable}, schema={self.schema})"

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

    def to_json(self, *, indent: Optional[int] = None) -> str:
        return json.dumps(list(self), indent=indent)

    @classmethod
    def from_json(cls, json_str: str, *, schema: Optional[Dict[str, Type]] = None, schema_add_missing: bool = False, schema_constrain_to_existing: bool = False, immutable: bool = False) -> 'listofdicts':
        data = json.loads(json_str)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("JSON must represent a list of dicts.")
        return cls(data, immutable=immutable, schema=schema, schema_add_missing=schema_add_missing, schema_constrain_to_existing=schema_constrain_to_existing)

    @classmethod
    def as_llm_prompt(cls, system_prompts, user_prompts, schema:dict = {'role': str, 'content': str}, *prompt_modes ) -> 'listofdicts':
        if type(system_prompts)==str: system_prompts=[system_prompts]
        if type(user_prompts)==str: user_prompts=[user_prompts]
        newobj = cls(immutable=False, schema=schema, schema_add_missing=True, schema_constrain_to_existing=False)

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

 

