# listofdicts

[![PyPI version](https://img.shields.io/pypi/v/listofdicts.svg)](https://pypi.org/project/listofdicts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


**Enterprise-grade strongly-typed [list of dictionaries] for Python**

---

## Summary

`listofdicts` is a powerful custom Python list-of-dicts data structure designed for modern AI automation, data processing, data pipelines, API layers, and JSON-based applications where structured lists of dictionaries are commonly used.

---

## Key Features

- ✅ Restrict types to list of dictionary objects
- ✅ Optional schema validation.
- ✅ Optional immutability (lock data after loading).
- ✅ Full JSON serialization/deserialization.
- ✅ Supports deep copying and safe mutations.
- ✅ Strict runtime type safety.
- ✅ Merge and update support.

---

## Installation

```bash
pip install listofdicts
```

## Usage

```python
from listofdicts import listofdicts

# Define schema for safety
schema = {
    'id': int,
    'name': str,
    'active': bool
}

lod = listofdicts([
    {'id': 1, 'name': 'Alice', 'active': True},
    {'id': 2, 'name': 'Bob', 'active': False}
], schema=schema)

# Append valid
lod.append({'id': 3, 'name': 'Carol', 'active': True})

# Partial update
lod.update_item(0, {'active': False})

# Merge with another listofdicts
lod2 = listofdicts([
    {'id': 4, 'name': 'Eve', 'active': True}
], schema=schema)

merged = lod.merge(lod2)

# Serialize to JSON
json_str = merged.to_json(indent=2)

# Deserialize from JSON
restored = listofdicts.from_json(json_str, schema=schema)

print(restored)
```



## API Summary
<table>
<tr><td><b>Method   </b></td><td><b>Description</b></td>
<tr><td>append()	    </td><td>Append a validated dictionary</td>
<tr><td>extend()	    </td><td>Extend with another </td>listofdicts
<tr><td>merge()   	    </td><td>Merge two instances</td>
<tr><td>update_item()	</td><td>Partially update an entry</td>
<tr><td>copy()	        </td><td>Deep copy</td>
<tr><td>as_mutable()	</td><td>Return mutable copy</td>
<tr><td>as_immutable()	</td><td>Return immutable copy</td>
<tr><td>to_json()	    </td><td>Serialize to JSON</td>
<tr><td>from_json()	    </td><td>Deserialize from JSON</td>
<tr><td>immutable	    </td><td>Property to check mutability</td>
<tr><td>schema	        </td><td>Property to access schema</td>
</table>

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