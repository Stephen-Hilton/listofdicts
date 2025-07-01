from listofdicts import listofdicts
import pytest, random

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

    # Immutable object:
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "link", "legs":4}, 
                       {"cat": "stumpy", "legs":3}], immutable=True)
    assert lod[0]["cat"] == "zelda"
    assert lod[1]["cat"] == "link"
    assert lod[2]["cat"] == "stumpy"
    with pytest.raises(TypeError): lod.append({"cat": "errorcat", "legs":4})

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
    with pytest.raises(TypeError): lod = lod + {"kid": "errorkid", "favorite color":"red"}
    
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

    # wrong value types
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

