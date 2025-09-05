from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )

from listofdicts import listofdicts

def test_can_initialize():
    obj = listofdicts([{"key": "value"}])
    assert isinstance(obj, listofdicts)

def test_usage():

    # build mutable LOD:
    lod = listofdicts([{"dog": "sunny"}])
    assert lod[0]["dog"] == "sunny"

    lod += {"dog": "luna"}
    assert lod[1]["dog"] == "luna"

    lod.extend(listofdicts([{"dog": "stella"}]))
    assert lod[2]["dog"] == "stella"

    for l in lod: print(l['dog'])


    # APPEND ONLY LoD
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "stumpy", "legs":3}], append_only=True)
    assert lod[0]["cat"] == "zelda"
    assert lod[1]["cat"] == "link"
    assert lod[2]["cat"] == "stumpy"
    assert lod.append({"cat": "appendcat", "legs":4}) == None
    assert lod[3]["cat"] == "appendcat"
    
    # append_only, updates not allowed -- neither the list nor the dictionaries
    assert len(lod) == 4 
    with pytest.raises(AttributeError): lod[3]["cat"] = "errorcat" 
    with pytest.raises(AttributeError): lod[3]["legs"] -= 1
    with pytest.raises(AttributeError): lod[3].update({"cat":"errorcat"})  
    with pytest.raises(AttributeError): lod[3] = lod[3] | {"spots":False}  
    with pytest.raises(AttributeError): lod[3] = {**lod[3], **{"spots":False}}  
    with pytest.raises(AttributeError): lod[3] = lod[3]
    assert len(lod) == 4 

    # appends still work tho:
    lod.append({"cat": "mutantcat", "legs":5}) 
    lod += {"cat": "zombiecat", "legs":3.5}
    lod.extend( [{"cat": "frankencat", "legs":8}] )
    lod = lod + [{"cat": "catmat", "legs":0}]
    assert len(lod) == 8

    # The only way to "turn off" append_only is to create a new deep copy of the object.
    # This can be done using using:  lod2 = lod.copy(append_only=False)
    # or the helper function,  lod2 = lod.as_mutable()
    lod2 = lod.copy(append_only=False)
    assert lod2.append_only == False
    # now these will all work:
    lod2[3]["cat"] = "errorcat" 
    lod2[3]["legs"] -= 1
    lod2[3].update({"cat":"errorcat"})  
    lod2[3] = lod[3] | {"spots":False}  
    lod2[3] = {**lod[3], **{"spots":False}}  
    # lod[3] is still an ImmutableDict, so you'll have to cast back to regular dict for this to work:
    lod2[3] = dict(lod[3]) 

    # or:
    lod2 = lod.as_mutable()
    assert lod2.append_only == False
    # now these will all work:
    lod2[3]["cat"] = "errorcat" 
    lod2[3]["legs"] -= 1
    lod2[3].update({"cat":"errorcat"})  
    lod2[3] = lod[3] | {"spots":False}  
    lod2[3] = {**lod[3], **{"spots":False}}  
    # lod[3] is still an ImmutableDict, so you'll have to cast back to regular dict for this to work:
    lod2[3] = dict(lod[3]) 

    # you can go from mutable to append_only using the same copy() method, or with:
    lod3 = lod2.as_append_only()
    assert lod3.append_only == True
    assert len(lod3) == 8
    assert lod3.append({"cat": "errorcat", "legs":4}) == None # append OK
    with pytest.raises(AttributeError): lod3[0]["legs"] -= 1  # updates NOT
    assert len(lod3) == 9




    # IMMUTABLE objects are similar, but don't allow additions either:
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "link", "legs":4}, 
                       {"cat": "stumpy", "legs":3},
                       {"cat": "mutantcat", "legs":5} ], immutable=True)
    assert lod[0]["cat"] == "zelda"
    assert lod[1]["cat"] == "link"
    assert lod[2]["cat"] == "stumpy"
    assert lod[3]["cat"] == "mutantcat"
 
    # no updates:
    assert len(lod) == 4
    with pytest.raises(AttributeError): lod[3]["cat"] = "errorcat" 
    with pytest.raises(AttributeError): lod[3]["legs"] -= 1
    with pytest.raises(AttributeError): lod[3].update({"cat":"errorcat"})  
    with pytest.raises(AttributeError): lod[3] = lod[3] | {"spots":False}  
    with pytest.raises(AttributeError): lod[3] = {**lod[3], **{"spots":False}}  
    with pytest.raises(AttributeError): lod[3] = lod[3]
    assert len(lod) == 4 

    # also no appends:
    with pytest.raises(AttributeError): lod.append({"cat": "mutantcat", "legs":5}) 
    with pytest.raises(AttributeError): lod += {"cat": "zombiecat", "legs":3.5}
    with pytest.raises(AttributeError): lod.extend( [{"cat": "frankencat", "legs":8}] )
    with pytest.raises(AttributeError): lod = lod + [{"cat": "catmat", "legs":0}]
    assert len(lod) == 4

    # The only way to "turn off" immutable is to create a new deep copy of the object.
    # This can be done using using:  lod2 = lod.copy(immutable=False)
    # or the helper function,  lod2 = lod.as_mutable()
    lod2 = lod.copy(immutable=False)
    # now these will all work:
    lod2.append({"cat": "mutantcat", "legs":5}) 
    lod2 += {"cat": "zombiecat", "legs":3.5}
    lod2.extend( [{"cat": "frankencat", "legs":8}] )
    lod2 = lod2 + [{"cat": "catmat", "legs":0}]
    assert len(lod2) == 8


    # you can go from mutable to immutable using the same copy() method, or with:
    lod3 = lod2.as_immutable()
    assert lod3.immutable == True
    assert len(lod3) == 8
    with pytest.raises(AttributeError): lod3.append({"cat": "errorcat", "legs":4}) == None # NO appends
    with pytest.raises(AttributeError): lod3[0]["legs"] -= 1  # NO updates
    assert len(lod3) == 8



    # append / extend functions
    lod = listofdicts([{"kid": "susie", "favorite color":"blue"},
                       {"kid": "joe", "favorite color":"green"}])
    lod.append({"kid": "bob", "favorite color":"yellow"})

    lod.extend(listofdicts([{"kid": "jane", "favorite color":"orange"}]))
    assert lod[0]["kid"] == "susie"
    assert lod[1]["kid"] == "joe"
    assert lod[2]["kid"] == "bob"
    assert lod[3]["kid"] == "jane"

    lod = lod + listofdicts([{"kid": "raul", "favorite color":"blue"}])
    lod += {"kid": "divya", "favorite color":"yellow"}
    lod += listofdicts([{"kid": "gustav", "favorite color":"white"}])
    assert lod[0]["kid"] == "susie"
    assert lod[1]["kid"] == "joe"
    assert lod[2]["kid"] == "bob"
    assert lod[3]["kid"] == "jane"
    assert lod[4]["kid"] == "raul"
    assert lod[5]["kid"] == "divya"
    assert lod[6]["kid"] == "gustav"
    
    # the "+" extends, and needs to be a list type, not a dict type:
    with pytest.raises(TypeError): lod = lod + {"kid": "errorkid", "favorite color":"red"}
    lod = lod + [{"kid": "errorkid", "favorite color":"red"}]
    
    # USAGE: SCHEMAS
    schema = {'dog': str, 'tail':bool, 'legs':int}
    lod = listofdicts([{"dog": "sunny", 'legs':4, 'tail':True}], schema=schema)
    lod.append({"dog": "luna", 'legs':4, 'tail':True})
    with pytest.raises(TypeError): lod.append({"dog": "errordog", 'legs':4}) # missing tail key
    assert lod[0]["dog"] == "sunny"
    assert lod[1]["dog"] == "luna"

    lod2 = listofdicts([{"dog": "stella", 'legs':4, 'tail':True},
                        {"dog": "fido", 'legs':4, 'tail':False},
                        {"dog": "rex", 'legs':4}] )
    with pytest.raises(TypeError):  lod.extend(lod2) # missing tail key
    assert len(lod) == 2 # didn't insert the above

    lod.schema_add_missing = True  # now add any missing keys, with None value
    lod.extend(lod2)
    assert lod[0]["dog"] == "sunny"
    assert lod[1]["dog"] == "luna"
    assert lod[2]["dog"] == "stella"
    assert lod[3]["dog"] == "fido"
    assert lod[4]["dog"] == "rex"
    assert len(lod) == 5
    assert lod[4]["tail"] == None

    # wrong value types (legs / tail / tail)
    with pytest.raises(TypeError): lod += {"dog": "errordog", 'legs':'4', 'tail':True} 
    with pytest.raises(TypeError): lod += {"dog": "errordog", 'legs':4, 'tail':'True'} 
    with pytest.raises(TypeError): lod += {"dog": "errordog", 'legs':4, 'tail':1} 

    # note, this only matters if there is a schema defined
    lod.schema = None 
    lod += {"dog": "errordog1", 'legs':'4', 'tail':True} 
    lod += {"dog": "errordog2", 'legs':4, 'tail':'True'} 
    lod += {"dog": "errordog3", 'legs':4, 'tail':1} 
    assert len(lod) == 8
    assert type(lod[5]['tail']) == bool
    assert type(lod[6]['tail']) == str
    assert type(lod[7]['tail']) == int
    
    # you cannot apply a new schema or schema parameters unless all data complies:
    with pytest.raises(TypeError): lod.schema = schema
    lod.schema_constrain_to_existing = False
    lod.schema = {'dog': str} # you can however reduce the scope of the schema
    assert lod.schema == {'dog': str}   
    assert len(lod) == 8

    # however, you can't apply "constrain to existing" if existing data will violate the rule
    with pytest.raises(TypeError): lod.schema_constrain_to_existing = True

    # to make this change, you have to fix your data:
    for d in lod:
        d['legs'] = int(d['legs'])
        d.pop('tail')

    assert all([len(d)==2 for d in lod])
    assert all([type(d['legs'])==int for d in lod])

    # with data fixed, this should now work:
    lod.schema = {'dog': str, 'legs':int}
    lod.schema_constrain_to_existing = True

    # there are no restrictions on changing "add missing" setting, as it only adds if needed, not removes
    lod.schema_add_missing = True
    lod.schema_add_missing = False
    lod.schema_add_missing = True
    

    # add missing keys, will create keys with None value
    lod = listofdicts.from_json('[{"snack":"chips", "type":"salty"}, {"snack":"cookies", "type":"sweet"}]',
                                schema={'snack':str, 'type':str, 'calories':int},
                                schema_add_missing=True,
                                schema_constrain_to_existing=False)
    assert len(lod) == 2
    assert all(['calories' in d for d in lod])     

    lod.schema={'snack':str, 'type':str, 'calories':int, 'new':bool} # added 'new' key
    assert all(['new' in d for d in lod]) # immediately added to all dicts, because schema_add_missing=True    

    lod.clear()
    assert len(lod) == 0


    lod = listofdicts()
    for i in range(1,101):
        lod.append({'order':i, 'randint':random.randint(1,100), 'randfloat':random.random()})
    assert len(lod) == 100

    for keyname in ['randfloat', 'order', 'randint']:
        lod.sort(keyname)
        prev = 0
        for d in lod:
            assert d[keyname] >= prev # current should always he larger or equal to previous
            prev = d[keyname]

    # new lod with metadata set at instantiation time:
    md = {'key1':1, 'key2':2}
    lod = listofdicts(metadata=md)
    assert lod.metadata == md
    assert len(lod) == 0

    # from_json ()
    data = [{"dog": "sunny"}, {"dog": "luna"}, {"dog": "stella"}, {"dog": "fido"}, {"dog": "rex"}]
    json_doc = json.dumps(data)

    lod = listofdicts.from_json(json_doc)
    assert len(lod) == 5
    assert lod[0]['dog'] == "sunny"
    assert lod[1]['dog'] == "luna"
    assert lod[2]['dog'] == "stella"
    assert lod[3]['dog'] == "fido"
    assert lod[4]['dog'] == "rex"

    # from_json (preserve_metadata=True)
    schema = {'dog': str}
    data = [{"dog": "sunny"}, {"dog": "luna"}, {"dog": "stella"}, {"dog": "fido"}, {"dog": "rex"}]
    metadata = {'key1':1, 'key2':2}

    lod = listofdicts.from_json(data, metadata=metadata, schema=schema, immutable=True)
    assert lod.schema == schema
    assert lod.metadata == metadata
    assert list(lod) == data
    assert lod.immutable == True
    
    full_json_doc = lod.to_json(preserve_metadata=True)
    assert type(full_json_doc) == str
    lod = None 
    lod = listofdicts.from_json(full_json_doc)
    assert lod.schema == schema
    assert lod.metadata == metadata
    assert list(lod) == data
    assert lod.schema['dog'] == str
    assert lod.immutable == True


def test_integrations():
    # pydantic:
    from pydantic import BaseModel 

    class Dog(BaseModel):
        name: str
        age: int
        limbs: listofdicts

    sparky = Dog(
        name='Sparky',
        age=3,
        limbs=listofdicts([
            {'name':'front left', 'length':10},
            {'name':'front right', 'length':10},
            {'name':'back left', 'length':10},
            {'name':'back right', 'length':10} ])
        )
    assert isinstance(sparky.limbs, listofdicts)    
    
if __name__ == '__main__':
    test_usage()