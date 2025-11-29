import json
import os
from datetime import datetime
from decimal import Decimal
import pytest

import fupi
from listofdicts import ListOfDicts
  

def test_import():
    # Test that the package is importable
    import listofdicts
    assert hasattr(listofdicts, 'ListOfDicts')
 
 
def test_from_json_with_single_dict():
    normal_data = json.dumps({"data": [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]})
    dict_data = json.dumps({'a':11, 'b':12})
    list_data = json.dumps([{'a':21, 'b':22}, {'c':23, 'd':24}])

    for i, tst in enumerate([normal_data, dict_data, list_data]):
        lod = ListOfDicts().from_json(tst)
        assert isinstance(lod, ListOfDicts)
        assert 'a' in lod[0]
        assert lod.a - (i*10) == 1
        assert lod.b - (i*10) == 2


def test_initialization_with_data():
    testdata = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    testmeta = {'source': 'unit_test', 'version': 1.0}
    lod1 = ListOfDicts(*testdata, metadata=testmeta)
    lod2 = ListOfDicts({'a': 1, 'b': 2}, {'a': 3, 'b': 4}, metadata={'source': 'unit_test', 'version': 1.0})
    assert lod1 == lod2
    lod3 = ListOfDicts(testdata).udpate_metadata(**testmeta)
    lod4 = ListOfDicts({'a': 1, 'b': 2}, {'a': 3, 'b': 4}).udpate_metadata(source='unit_test', version=1.0)
    assert lod3 == lod4
    assert lod1 == lod2 == lod3 == lod4


def test_callback_on_sync():

    lod = ListOfDicts({'a': 1, 'b': 2},
                      {'a': 3, 'b': 4}, 
                      {'a': 5, 'b': 6},
                      {'a': 7, 'b': 8},
                      {'a': 9, 'b': 10})
    
    # call back called when "active" data changed:
    square_value = None

    def print_changed_data(self, change_dict):
        print(f"data changed: {change_dict}, full data: {dict(self[self.active_index])}")
        nonlocal square_value
        square_value = change_dict['a'] **2

    lod.callback_on_change( print_changed_data )
    lod.a = 1
    assert square_value == 1
    lod.a = 2
    assert square_value == 4
    lod.a = 3
    assert square_value == 9

    # or via lambda: 
    lod.callback_on_change( lambda self, change_dict: print(f"Lambda callback: data changed: {change_dict}") )
    lod.a = 3
    lod.a = 2
    lod.a = 1


    # "self" is the ListOfDicts instance, so we can access non-data elements, like active_index"
    def square_active_index(self, change_dict):
        nonlocal square_value
        square_value = self.active_index **2

    lod.callback_on_change( square_active_index )
    lod.active_index = 0
    assert square_value == 0
    lod.active_index = 1
    assert square_value == 1
    lod.active_index = 2
    assert square_value == 4
    lod.active_index = 3
    assert square_value == 9
    lod.active_index = 4
    assert square_value == 16

    # accessing the ListOfDicts instance means you can enforce rules
    def always_stay_on_index_3(self, change_dict):
        if self.active_index != 3: # this is important to avoid infinite loop
            self.active_index = 3   

    lod.callback_on_change( always_stay_on_index_3 )
    lod.active_index = 0
    assert lod.active_index == 3
    lod.active_index = 1
    assert lod.active_index == 3
    lod.active_index = 2
    assert lod.active_index == 3
    lod.active_index = 4
    assert lod.active_index == 3

    # or, validate data types:
    def must_be_positive_a(self, change_dict):
        nonlocal prev_a
        if 'a' in change_dict and change_dict['a'] < 0:  self.a = prev_a
        else:   prev_a = change_dict['a']
    prev_a = None

    lod.callback_on_change( must_be_positive_a )
    lod.a = 5
    assert lod.a == 5
    lod.a = -10
    assert lod.a == 5  # should have reverted
    lod.a = 3
    assert lod.a == 3
    lod.a = -1
    assert lod.a == 3  # should have reverted
    lod.a = 0
    assert lod.a == 0

    # you can also "disable" the callback for loads:
    def my_fancy_callback(self, change_dict):
        nonlocal _loading 
        if _loading: return # skip if loading

        if 'c' in change_dict: return # avoid infinite recursion 
        self.c = self.a + self.b
    _loading = False

    # new lod object:
    lod = ListOfDicts({'a': 1, 'b': 2},
                      {'a': 3, 'b': 4}, 
                      {'a': 5, 'b': 6},
                      {'a': 7, 'b': 8},
                      {'a': 9, 'b': 10})
    lod.callback_on_change(my_fancy_callback)
    lod.a = 1
    assert lod.c == 3  # 1 + 2
    lod.a = 2
    assert lod.c == 4  # 2 + 2
    
    _loading = True  # simulate loading
    lod.a = 3
    assert lod.c == 4   # should not change, callback disabled
    _loading = False  # re-enable callback
    lod.c = 5  # manually set c, since callback was disabled
    assert lod.c == 5  # should now be 3 + 2
    lod.c = 4  # reset c to 4 (allowed in callback)
    lod.a = lod.a # or, you can trigger the callback by setting a to itself
    assert lod.c == 5  # should now be 3 + 2
    lod.a = 4
    assert lod.c == 6  # 4 + 2

    # this can be important, as set-level changes will also trigger the callback:
    lod.append({'a': 11, 'b': 12})
    lod.active_index = -1 # last, aka what we just added
    assert lod.c == 23  # 11 + 12

    # you may not want to trigger for every change:
    _loading = True
    for r in lod: r['a'] = 5
    _loading = False
    assert lod.a == 5
    assert lod.b == 12
    assert lod.c == 23 # update was skipped, so this is incorrect 
    lod.a = 6 
    assert lod.c == 18 # updated on next change




def test_active_index_and_active_row():
    lod = ListOfDicts({'a': 1}, {'a': 2}, {'a': 3})
    assert lod.active_index == 0
    assert lod.active_row == {'a': 1}

    lod.active_index = 1
    assert lod.active_index == 1
    assert lod.active_row == {'a': 2}

    lod.active_index = 2
    assert lod.active_index == 2
    assert lod.active_row == {'a': 3}

    lod.clear()
    assert lod.active_index is None
    assert lod.active_row is None


def test_append_and_active_sync():
    lod = ListOfDicts()
    lod.append({'a': 1, 'b': 2})
    assert lod.active_index == 0
    # attributes should be accessible and sync from active dict
    assert lod.a == 1
    assert lod.b == 2

    lod.append({'a': 3, 'b': 4})
    # switch active index
    lod.active_index = 1
    assert lod.a == 3
    assert lod.b == 4


def test_append_type_error():
    lod = ListOfDicts()
    with pytest.raises(TypeError):
        lod.append(123)


def test_insert_and_index_adjust():
    lod = ListOfDicts({'x': 1}, {'x': 2})
    assert lod.active_index == 0
    lod.insert(0, {'x': 99})
    # active index should have been incremented
    assert lod.active_index == 1
    assert lod.x == 1


def test_extend_type_check():
    lod = ListOfDicts()
    with pytest.raises(TypeError):
        lod.extend([{'a': 1}, 2])


def test_make_datatypes_dbsafe_and_pyobj():
    dt = datetime(2020, 1, 2, 3, 4, 5)
    lod = ListOfDicts({'f': 1.5, 't': dt, 'nested': {'n': 2.5}, 'arr': [1.1, dt]})

    dbsafe = lod.make_datatypes_dbsafe()
    # floats become Decimal, datetimes become strings
    assert isinstance(dbsafe[0]['f'], Decimal)
    assert isinstance(dbsafe[0]['t'], str)
    assert isinstance(dbsafe[0]['nested']['n'], Decimal)
    assert isinstance(dbsafe[0]['arr'][0], Decimal)
    assert isinstance(dbsafe[0]['arr'][1], str)

    # Convert back to python objects
    pyobj = dbsafe.make_datatypes_pyobj()
    assert isinstance(pyobj[0]['f'], float)
    # datetime strings without Z should convert back
    assert isinstance(pyobj[0]['t'], datetime)

    # strings with trailing Z are parsed to datetime in this environment
    lod2 = ListOfDicts({'d': '2020-01-01T00:00:00Z'})
    converted = lod2.make_datatypes_pyobj()
    assert isinstance(converted[0]['d'], datetime)


def test_to_json_and_from_json():
    lod = ListOfDicts({'a': 1, 'ts': datetime(2021, 5, 4, 12, 0)})
    lod.metadata = {'m': 'v'}
    j = lod.to_json()
    assert 'metadata' in j
    assert 'data' in j

    # create a JSON payload that includes a date string and ensure from_json parses it
    payload = json.dumps({'metadata': {'k': 'v'}, 'data': [{'d': '2022-01-02T03:04:05'}]})
    newlod = ListOfDicts().from_json(payload)
    # make_datatypes_pyobj should have converted the date string to datetime
    assert isinstance(newlod[0]['d'], datetime)



def test_addkey_if_missing():
    lod = ListOfDicts({'a': 1}, {'a': 2, 'b': 3})
    lod.addkey_if_missing('b', value_if_missing=0)
    assert lod[0]['b'] == 0
    assert lod[1]['b'] == 3

    lod.addkey_if_missing(['c', 'd'], value_if_missing=None)
    assert 'c' in lod[0] and 'd' in lod[0]


def test_insert_type_error_and_inplace_conversions():
    lod = ListOfDicts({'f': 1.1, 't': datetime(2020, 1, 1)})
    with pytest.raises(TypeError):
        lod.insert(0, 123)

    # inplace dbsafe
    lod.make_datatypes_dbsafe(inplace=True)
    assert isinstance(lod[0]['f'], Decimal)

    # inplace pyobj
    lod.make_datatypes_pyobj(inplace=True)
    assert isinstance(lod[0]['f'], float)


def test_make_datatypes_pyobj_valueerror_and_sync_edge_cases():
    # ValueError during fromisoformat should return original string
    lod = ListOfDicts({'d': '2020-02-30T00:00:00'})
    converted = lod.make_datatypes_pyobj()
    assert isinstance(converted[0]['d'], str)

    # _sync_from_dict early return when _syncing True
    lod2 = ListOfDicts({'a': 1})
    lod2._syncing = True
    lod2._sync_from_dict()
    assert lod2._syncing is True
    lod2._syncing = False

    # _sync_to_dict early return when empty
    empty = ListOfDicts()
    # should not raise
    empty._sync_to_dict('k', 'v')


def test_setitem_and_delitem_sync_branches():
    lod = ListOfDicts({'a': 1})
    # setting item to dict at active index triggers sync
    lod[0] = {'a': 9}
    assert lod.a == 9

    # deleting active index triggers sync to new state
    lod2 = ListOfDicts({'a': 1}, {'b': 2})
    lod2.active_index = 0
    del lod2[0]
    # now active item should be the former index 1
    assert hasattr(lod2, 'b') and not hasattr(lod2, 'a')


def test_getattribute_exception_handling():
    lod = ListOfDicts({'a': 1})
    # force an out-of-range active index to provoke IndexError inside __getattribute__
    lod._active_index = 99
    # should not raise; getattr with default should return default
    assert getattr(lod, 'does_not_exist', None) is None


def test_make_datatypes_pyobj_leaves_ints():
    lod = ListOfDicts({'n': 7})
    converted = lod.make_datatypes_pyobj()
    assert isinstance(converted[0]['n'], int)


def test_setitem_and_type_error():
    lod = ListOfDicts({'a': 1})
    with pytest.raises(TypeError):
        lod[0] = 5


def test_delitem_pop_clear_behavior():
    lod = ListOfDicts({'a': 1}, {'a': 2}, {'a': 3})
    lod.active_index = 2
    # delete an earlier item should decrement active_index
    del lod[0]
    assert lod.active_index == 1

    # pop the last
    val = lod.pop()
    assert isinstance(val, dict)
    # after pop, ensure sync
    # clear resets active_index to None
    lod.clear()
    assert lod.active_index is None


def test_setattr_sync_and_exclusion_of_class_attrs():
    class MyLOD(ListOfDicts):
        my_attr: str = None

    mlod = MyLOD({'a': 1})
    # my_attr defined as class attr should be in _class_attrs
    assert 'my_attr' in mlod._class_attrs

    # setting a normal attribute syncs to dict
    mlod.b = 5
    assert mlod[0]['b'] == 5

    # setting a class-attribute name should not write into the dict
    mlod.my_attr = 'hello'
    assert 'my_attr' not in mlod[0]


def test_getattribute_and_private_setattr():
    lod = ListOfDicts({'x': 1})
    # private attribute shouldn't attempt to sync
    lod._private = 99
    assert not ('_private' in lod[0])
    # attribute access should pull from active dict
    assert lod.x == 1


def test_active_index_setter_validation():
    lod = ListOfDicts({'a': 1}, {'a': 2})
    with pytest.raises(TypeError):
        lod.active_index = 'not-an-int'
    with pytest.raises(IndexError):
        lod.active_index = 99
    # negative index wraps
    lod.active_index = -1
    assert lod.active_index == 1


def test_str_contains_json_and_repr():
    lod = ListOfDicts({'a': 1})
    s = str(lod)
    assert 'ListOfDicts(' in s
    assert 'metadata' in s


def test_inheritance_and_classvar_exclusion():
    # test class level inheritance:
    class MyListOfDicts(ListOfDicts):
        # class variables are specifically excluded from instance data
        # ONLY if declared at class level, like this: 
        my_var1:str = None 
        my_var2:str = None 

        def __init__(self, *args):
            super().__init__(*args)
            self.my_var1:str = 'foo'
            self.my_var2:str = 'bar'
            self.my_var3:str = 'baz'  # instance var, should appear in data
            # Note, added to the FIRST data item only
    
    mlod = MyListOfDicts({'a':1, 'b':2, 'c':3},
                         {'a':4, 'b':5, 'c':6},
                         {'a':7, 'b':8, 'c':9})
    mlod.metadata = {'state':'all good', 'confidence': 'hope'}

    assert len(mlod) == 3
    assert mlod.active_index == 0
    assert mlod.a == 1
    assert mlod.b == 2
    assert mlod.c == 3
    assert mlod.my_var1 == 'foo'      # class vars WILL NOT appear in data
    assert mlod.my_var2 == 'bar'      # class vars WILL NOT appear in data
    assert not ('my_var1' in mlod[0]) # class vars WILL NOT appear in data
    assert not ('my_var2' in mlod[0]) # class vars WILL NOT appear in data

    assert mlod.my_var3 == 'baz' 
    assert 'my_var3' in mlod[0]  # instance var WILL appear in data
    assert len(mlod[mlod.active_index]) == 4 # should exclude class vars
    print(mlod)


def test_example_usage():

    # Example usage / tests
    lod = ListOfDicts()
    lod.append({'a': 1, 'b': 2})
    lod.append({'a': 3, 'b': 4})
    lod.append({'a': 5, 'b': 6})
    
    lod.active_index = 0
    assert lod.a == 1
    assert lod.b == 2
    assert lod[0]['a'] == 1
    assert lod[0]['b'] == 2

    lod.active_index = 1
    assert lod.a == 3
    assert lod.b == 4

    lod.active_index = 2
    assert lod.a == 5
    assert lod.b == 6

    # normal list-of-dict operations still work:
    assert lod[0]['a'] == 1
    assert lod[0]['b'] == 2
    assert lod[1]['a'] == 3
    assert lod[1]['b'] == 4
    assert lod[2]['a'] == 5
    assert lod[2]['b'] == 6
    assert len(lod) == 3
    assert len(lod[0]) == 2 
    assert len(lod[1]) == 2
    assert len(lod[2]) == 2
    assert isinstance(lod, list)
    assert isinstance(lod, ListOfDicts)
    assert isinstance(lod[0], dict)

    # add new the normal way:
    lod[0]['c'] = 7
    lod.active_index = 0
    assert lod.c == 7

    # add new using simplified method:
    lod.d = 8
    assert lod.d == 8
    assert lod[0]['d'] == 8

    # you still must add new rows using normal list methods:
    lod.append({'a': 9})
    assert lod[3]['a'] == 9
    # after which the above logic applies:
    lod.active_index = len(lod)-1
    assert lod.a == 9
    lod.b = 10
    assert lod.b == 10
    assert lod[3]['b'] == 10

    lod.extend([{'a': 11}, {'a': 12}])
    lod.active_index = 4
    assert lod.a == 11
    lod.active_index = 5
    assert lod.a == 12
    lod.b = 13
    assert lod.b == 13
    assert lod[5]['b'] == 13

    lod.clear() # remove all unused properties
    assert lod == [] 
    assert lod.active_index is None # always None if empty
    assert hasattr(lod, 'a') == False
     
    lod.append({'a': 1, 'b': 2})
    assert lod.active_index == 0
    assert lod.a == 1 
    
    lod.pop() # should now be empty
    assert lod.active_index is None # always None if empty
    assert lod == [] 
    assert hasattr(lod, 'a') == False

    lod.append({'a': 1, 'b': 2})
    lod.append({'c': 3, 'd': 4})
    lod.active_index = 0
    assert lod.a == 1 # index 0 has 'a' 

    lod.active_index = 1
    assert lod.c == 3
    assert hasattr(lod, 'a') == False   # index 0 does not have 'a'


def test_from_json_invalid_raises_valueerror():
    """Test that invalid JSON content (e.g., non-dict elements) raises ValueError with helpful message."""
    import pytest
    lod = ListOfDicts({'a': 1})
    
    # Test with JSON that has a list of non-dict items (which will fail extend)
    with pytest.raises(ValueError, match="Invalid JSON content"):
        lod.from_json('[1, 2, 3]')  # integers are not dicts, will fail

pass