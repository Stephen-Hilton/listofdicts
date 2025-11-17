# ListOfDicts

A Python list subclass that provides convenient attribute-based access to dictionary items, with seamless synchronization between active dict properties and object attributes. Includes JSON serialization, datatype conversion utilities, and full type validation.

## Features

- **Attribute-based access**: Access active dictionary keys as object attributes
- **Active index tracking**: Track and switch between items in the list
- **Automatic syncing**: Changes to attributes sync to the active dictionary
- **Type validation**: All list items must be dictionaries
- **JSON serialization**: Serialize to/from JSON with metadata support
- **Datatype conversion**: Convert between Python objects (float, datetime) and database-safe types (Decimal, ISO strings)
- **Class attribute exclusion**: Subclass variables are automatically excluded from instance data
- **100% test coverage**: Comprehensive test suite with pytest

## Installation

```bash
pip install listofdicts
```

Or install from source:

```bash
git clone https://github.com/Stephen-Hilton/listofdicts.git
cd listofdicts
pip install -e .
```

### Development Installation

For development, install with test dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from listofdicts import ListOfDicts

# Create a new ListOfDicts
lod = ListOfDicts()

# Add dictionaries
lod.append({'a': 1, 'b': 2})
lod.append({'a': 3, 'b': 4})

# Access via active index
lod.active_index = 0
print(lod.a)  # Output: 1
print(lod.b)  # Output: 2

# Switch active index
lod.active_index = 1
print(lod.a)  # Output: 3

# Modify via attribute (syncs to dict)
lod.b = 99
print(lod[1]['b'])  # Output: 99
```

## Usage

### Creating and Populating

```python
from listofdicts import ListOfDicts

# Empty list
lod = ListOfDicts()

# Initialize with dictionaries (variadic args or lists)
lod = ListOfDicts(
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35}
)

# Standard list operations work normally
lod.append({'name': 'Diana', 'age': 28})
lod.insert(1, {'name': 'Eve', 'age': 27})
lod.extend([{'name': 'Frank', 'age': 32}])

# Type validation
try:
    lod.append("not a dict")  # Raises TypeError
except TypeError as e:
    print(f"Error: {e}")
```

### Active Index and Attribute Access

```python
lod = ListOfDicts(
    {'x': 1, 'y': 2},
    {'x': 10, 'y': 20},
    {'x': 100, 'y': 200}
)

# Set active index to access dict as attributes
lod.active_index = 0
print(lod.x, lod.y)  # Output: 1 2

# Switch active index
lod.active_index = 1
print(lod.x, lod.y)  # Output: 10 20

# Negative indices wrap around
lod.active_index = -1
print(lod.x, lod.y)  # Output: 100 200 (last item)

# Modify attributes (syncs to active dict)
lod.y = 999
print(lod[2]['y'])  # Output: 999

# Add new keys via attribute assignment
lod.z = 42
print(lod[2]['z'])  # Output: 42
print('z' in lod[2])  # Output: True
```

### Managing Keys

```python
lod = ListOfDicts(
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'},
    {'id': 3}  # Missing 'status' key
)

# Add missing keys to all dicts
lod.addkey_if_missing('status', value_if_missing='active')

print(lod[0])  # {'id': 1, 'name': 'Alice', 'status': 'active'}
print(lod[2])  # {'id': 3, 'status': 'active'}

# Add multiple keys at once
lod.addkey_if_missing(['email', 'verified'], value_if_missing=None)
```

### JSON Serialization

```python
from datetime import datetime
import json

lod = ListOfDicts({'id': 1, 'created': datetime.now()})
lod.metadata = {'version': '1.0', 'author': 'Alice'}

# Serialize to JSON (datetimes become ISO strings, floats become Decimals)
json_string = lod.to_json()
print(json_string)
# Output:
# {
#   "metadata": {
#     "version": "1.0",
#     "author": "Alice"
#   },
#   "data": [
#     {
#       "id": 1,
#       "created": "2025-01-15T10:30:45.123456"
#     }
#   ]
# }

# Deserialize from JSON
loaded = ListOfDicts().from_json(json_string)
print(isinstance(loaded[0]['created'], datetime))  # Output: True
print(loaded.metadata)  # Output: {'version': '1.0', 'author': 'Alice'}
```

### Datatype Conversion

Convert between Python objects and database-safe types:

```python
from datetime import datetime
from decimal import Decimal

lod = ListOfDicts({
    'price': 19.99,
    'quantity': 5,
    'timestamp': datetime(2025, 1, 15, 10, 30, 45)
})

# Convert to database-safe types (float→Decimal, datetime→ISO string)
db_safe = lod.make_datatypes_dbsafe()
print(type(db_safe[0]['price']))      # Output: <class 'decimal.Decimal'>
print(type(db_safe[0]['timestamp']))  # Output: <class 'str'>

# Convert back to Python objects
py_obj = db_safe.make_datatypes_pyobj()
print(type(py_obj[0]['price']))       # Output: <class 'float'>
print(type(py_obj[0]['timestamp']))   # Output: <class 'datetime.datetime'>

# In-place conversion (modifies original)
lod.make_datatypes_dbsafe(inplace=True)
print(type(lod[0]['price']))  # Output: <class 'decimal.Decimal'>
```

### Subclassing with Class Attributes

```python
class Person(ListOfDicts):
    # Class-level attributes are excluded from instance data
    species: str = 'Homo sapiens'
    
    def __init__(self, *args):
        super().__init__(*args)
        self.status = 'active'  # Instance attribute (appears in data)

# Create instance
people = Person(
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25}
)

people.active_index = 0
print(people.name)          # Output: 'Alice'
print(people.species)       # Output: 'Homo sapiens' (class var, not in data)
print(people.status)        # Output: 'active' (instance var, in data)
print('species' in people[0])  # Output: False
print('status' in people[0])   # Output: True
```

## API Reference

### Constructor

```python
ListOfDicts(*args)
```

Create a new ListOfDicts. Args can be:
- Individual dicts: `ListOfDicts({'a': 1}, {'b': 2})`
- A list/tuple: `ListOfDicts([{'a': 1}, {'b': 2}])`
- Mixed: `ListOfDicts({'a': 1}, [{'b': 2}])`

### Properties

#### `active_index`

Get or set the active dictionary index. Setting triggers synchronization.

```python
lod.active_index = 0  # Set active index
idx = lod.active_index  # Get current active index
```

**Raises:**
- `TypeError`: If value is not an integer
- `IndexError`: If index is out of range
- Negative indices wrap (e.g., `-1` is the last item)
- Returns `None` if the list is empty

### Methods

#### `append(item)`

Add a dictionary to the end of the list. First item added sets `active_index` to 0.

```python
lod.append({'key': 'value'})
```

**Raises:** `TypeError` if item is not a dict

#### `insert(index, item)`

Insert a dictionary at the given index. Adjusts `active_index` if needed.

```python
lod.insert(0, {'key': 'value'})
```

**Raises:** `TypeError` if item is not a dict

#### `extend(items)`

Add multiple dictionaries from an iterable.

```python
lod.extend([{'a': 1}, {'b': 2}])
```

**Raises:** `TypeError` if any item is not a dict

#### `addkey_if_missing(keys, value_if_missing=None)`

Add keys to all dictionaries in the list if they don't exist.

```python
lod.addkey_if_missing(['status', 'verified'], value_if_missing=None)
lod.addkey_if_missing('email', value_if_missing='')
```

**Returns:** `self` (chainable)

#### `make_datatypes_dbsafe(inplace=False)`

Convert float→Decimal and datetime→ISO string for database storage.

```python
db_safe = lod.make_datatypes_dbsafe()
lod.make_datatypes_dbsafe(inplace=True)  # Modify original
```

**Returns:** New ListOfDicts with converted types (or `self` if inplace=True, making it chainable).  Note, new ListOfDicts does NOT carry over class properties, like metadata.

#### `make_datatypes_pyobj(inplace=False)`

Convert Decimal→float and ISO strings→datetime for Python use.

```python
py_obj = lod.make_datatypes_pyobj()
lod.make_datatypes_pyobj(inplace=True)  # Modify original
```

**Returns:** New ListOfDicts with converted types (or `self` if inplace=True, making it chainable).  Note, new ListOfDicts does NOT carry over class properties, like metadata.

#### `to_json()`

Serialize to JSON string with metadata.

```python
json_str = lod.to_json()
```

**Returns:** JSON string

#### `from_json(json_content, metadata_to_props=[])`

Load ListOfDicts from a JSON string. This is an instance method (not class method), and will replace all existing instance data and metadata.

```python
lod = ListOfDicts().from_json(json_str)
```

**Parameters:**
- `json_content`: JSON string in the format `{"data":[...], "metadata":{...} }` (both `data` and `metadata` keys optional)

**Returns:** ListOfDicts with deserialized data

#### `clear()`

Remove all items and reset `active_index` to None.

```python
lod.clear()
```

#### `pop(index=-1)`

Remove and return item at index (default: last item).

```python
last = lod.pop()
first = lod.pop(0)
```

## Testing

The package includes 100% test coverage with pytest.

### Running Tests

```bash
# Install test dependencies
pip install pytest coverage

# Run all tests
pytest test/test_listofdicts.py -v

# Run with coverage report
python -m coverage run -m pytest test/test_listofdicts.py
python -m coverage report -m
```

### Test Examples

See `test/test_listofdicts.py` for comprehensive examples. Key test functions:

- `test_example_usage()` - Complete usage walkthrough
- `test_append_and_active_sync()` - Attribute synchronization
- `test_make_datatypes_dbsafe_and_pyobj()` - Datatype conversion
- `test_to_json_and_from_json()` - JSON serialization
- `test_inheritance_and_classvar_exclusion()` - Subclassing patterns

### Coverage

Current test coverage: **100%**

```
Name                             Stmts   Miss  Cover
------------------------------------------------------
src/ListOfDicts/__init__.py          0      0   100%
src/ListOfDicts/listofdicts.py     163      0   100%
test/test_listofdicts.py           224      0   100%
------------------------------------------------------
TOTAL                              387      0   100%
```

## Common Patterns

### Filtering and Iteration

```python
lod = ListOfDicts(
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35}
)

# Iterate over all items
for item in lod:
    print(item['name'], item['age'])

# Filter by condition
adults = [item for item in lod if item['age'] >= 30]

# Map with active index
for i, item in enumerate(lod):
    lod.active_index = i
    print(f"{lod.name} is {lod.age}")
```

### Batch Operations

```python
lod = ListOfDicts(
    {'id': 1, 'status': 'pending'},
    {'id': 2, 'status': 'pending'},
    {'id': 3, 'status': 'pending'}
)

# Update all items at once
for i in range(len(lod)):
    lod.active_index = i
    lod.status = 'approved'
```

### Working with Metadata
Metadata is a class variable, meaning it will never appear in the 'data' of the ListOfDicts. This also means that when creating a LOD object from data, the metadata isn't implicitly carried forward.  For example: 

```python
lod = ListOfDicts(
    {'id': 1, 'status': 'pending'},
    {'id': 2, 'status': 'pending'},
    {'id': 3, 'status': 'pending'}
)
lod.metadata = {'version':1.0}

newlod = lod[:] 
assert newlod.metadata == {}
```
The `lod[:]` command creates a new data object, but doesn't contain the metadata (or any other class variable), so it's not carried over.

Metadata is the only class variable that is included in the `.to_json()` and `.from_json()`  methods.  This does allow you to serialize / deserialize using JSON, and persist metadata.

```python
lod = ListOfDicts({'data': 'value'})
lod.metadata = {
    'version': '1.0',
    'created_by': 'Alice',
    'timestamp': '2025-01-15T10:30:45'
}

# Access metadata
print(lod.metadata['version'])

# Persist with metadata
json_str = lod.to_json()
restored = ListOfDicts().from_json(json_str)
print(restored.metadata)
```

## License

MIT License — see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure 100% test coverage
5. Submit a pull request

## Support

For issues and questions, please open a GitHub issue at:
https://github.com/Stephen-Hilton/listofdicts/issues
