# listofdicts

`listofdicts` is a Python container class that extends `List[Dict[str, Any]]` to provide:

- Optional **schema enforcement** with runtime type validation
- **Safe mutation** with immutability support
- **Deep JSON serialization/deserialization**
- **Custom metadata storage**
- Utilities for **sorting**, **copying**, and **prompt formatting** (LLM support)

This class is ideal for applications that require structured tabular-like data management in Python without external dependencies.

---

## 🚀 Features

- 🔒 **Immutability**: Optional full immutability, at both list and dict level
- 🔒 **Append_only**: Optional append-only protection, at both list and dict level
- ✅ **Schema validation**:
  - `schema_constrain_to_existing`: restrict keys to the schema
  - `schema_add_missing`: auto-insert missing schema keys as `None`
  - pydantic validation compliant
- 🔁 **Full list-like behavior**: slicing, appending, extending, sorting, copying, updating
- 🧠 **Metadata support**: Store additional metadata alongside your list of dicts
- 🔄 **JSON I/O**: Easily serialize/deserialize from JSON
- 🤖 **LLM prompt builder**: `as_llm_prompt` constructor with built-in prompt roles and tone presets

---

## 📦 Installation

[![PyPI version](https://img.shields.io/pypi/v/listofdicts.svg)](https://pypi.org/project/listofdicts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

 


## 🔧 Usage

```python
from listofdicts import listofdicts

data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]
 
lod = listofdicts(  data, 
                    schema = {"name": str, "age": int}, 
                    schema_constrain_to_existing = True, 
                    schema_add_missing = True)

lod.append({"name": "Carol", "age": 22})
lod += {"name":"Danny", "age":26}

try:
    lod += {"name":"Errorboy", "fingers":11}
except TypeError as te:
    print(f"schema set to constrain keys to existing, so this fails due to fingers.\n{te}")    

# you can add arbitrary metadata to the object:
lod.metadata = {"data_source":"some.test.location",
                "load_errors":1,
                "errors":[te]}

# iterate or enumerate core data (without metadata)
for person in lod:
    print(f" The person named {person['name']} is {person['age'] or 'unknown'} years old.")

# when seralizing to JSON, you can optionally keep the metadata.
# with metadata, you'll get {"data": [{core data}], "metadata": {optional metadata} }
# with no metadata, you'll only get [{core data}]
print(lod.to_json(indent=2, preserve_metadata=True))
```


## 📘 API Reference

### 🔧 Methods

| Method | Description |
|--------|-------------|
| `append` | Append a dictionary to the end of this listofdicts object. This will fail if the object has been made immutable, or if the schema was defined and enforced, and the new dictionary keys do not match the schema. |
| `as_immutable` | Returns an immutable deepcopy of this listofdicts instance. |
| `as_append_only` | Returns an append_only deepcopy of this listofdicts instance. |
| `as_mutable` | Returns a fully mutable deepcopy of this listofdicts instance. |
| `as_llm_prompt` | Creates a listofdicts instance, customized for LLM prompts. |
| `as_mutable` | Returns a mutable deepcopy of this listofdicts instance. |
| `clear` | Clear the listofdicts object (in place). This will fail if this object has been made immutable. |
| `copy` | Performs a deep copy of the listofdicts instance, with optional schema and immutability overrides. |
| `extend` | Extend THIS listofdicts object (in place) with dictionaries from another listofdicts object (returning None). This will fail if this object has been made immutable, or if the schema was defined and enforced, and the new dictionary keys do not match the schema. |
| `from_json` | Creates a listofdicts instance from a JSON string. |
| `pop` | Remove and return an element from the listofdicts object, at the given index (default last). This will fail if this object has been made immutable. |
| `popitem` | Remove and return an element from the listofdicts object. This will fail if this object has been made immutable. |
| `remove` | Remove an element from the listofdicts object (in place), by value (aka dictionary). This will fail if this object has been made immutable. |
| `sort` | Sort the order of dictionaries within the list by a given dictionary key, with the requirement that the key must be present in all dictionaries in the list. This does not affect the data, only its order within the list, and therefore can be called on immutable listofdicts objects. |
| `to_json` | Returns a JSON string representation of the listofdicts instance. If `preserve_metadata` is True, all metadata and other settings will be nested under a "metadata" key, and the core iterator data will be nested under a "data" key. If False, only the core data is returned. |
| `unique_key_values` | Returns a list of all unique values across all dicts in the listofdicts, for a given key. |
| `unique_keys` | Returns a list of all unique keys found in all dicts. |
| `update_item` | Updates the dictionary object of the list at the given index. Args: `index (int)` – index to update; `updates (Dict[str, Any])` – dictionary with updates. |
| `validate_all` | Validate all elements in the listofdicts object. Fails if the schema is enforced and any keys do not match the schema. Useful before applying a new schema. |
| `validate_item` | Validate a single dictionary element in the listofdicts object. Fails if the schema is enforced and keys do not match the schema. Useful for validating an item before insertion. |

---

### 🏷️ Properties

| Property | Description |
|----------|-------------|
| `metadata` |  Metadata is a dictionary of arbitrary key-value pairs to be stored with the listofdicts instance. This is intended to store information about the listofdicts instance that is not part of the core data. This is not exposed during object iteration or enumeration, but can be optionally serialized to JSON. |
| `schema` | Schema is a dictionary of key-type pairs that specifies the {KeyName: Type} of each key in the listofdicts, for example: {"key1": str, "key2": int, "key3": float}. This is used for runtime type enforcement and schema validation, using the two flag options: <br> - schema_constrain_to_existing: all data keys must exist in the schema. <br> - schema_add_missing: any data keys missing compared to the schema will be added with a value of None. |
| `schema_add_missing` | If set to True with a defined schema, any keys in the schema that are not present in the dictionary data will be added with a value of None. This is useful when adding new listofdicts elements, to ensure that all keys in the schema are present in the dictionary data. Note, this does NOT CONSTRAIN data keys to only keys defined in the schema, it only adds missing keys. To constrain data to only keys defined in the schema, set schema_constrain_to_existing to True. |
| `schema_constrain_to_existing` | If set to True with a defined schema, all keys in the dictionary data must also be present in the schema. This constrains data added to the listofdicts to only keys defined in the schema (if defined). Note, this does NOT REQUIRE all keys in the schema to be present in the dictionary data, it only enforces the constraint. To add missing keys when adding new listofdict elements, set schema_add_missing to True. |



## 🧪 Python Compatibility
Tested with Python 3.10+


## 📄 License
MIT License


## 👤 Author
Built by Stephen Hilton — Contributions welcome!


## Directory Structure
```
listofdicts/
    ├── src/
    │   ├── __init__.py
    │   └── listofdicts.py
    ├── tests/
    │   └── test_listofdicts.py
    ├── README.md
    ├── pyproject.toml
    ├── setup.cfg
    └── LICENSE
```