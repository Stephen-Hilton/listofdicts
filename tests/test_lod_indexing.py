from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts



def test_negative_indexes():
    data = [{"dog": "sunny", "legs": 4}, {"dog": "luna", "legs": 4}, {"dog": "stumpy", "legs": 3}, {"dog": "fido"}]
    lod = listofdicts.from_json(data)

    assert lod[0]['dog'] == "sunny"
    assert lod[1]['dog'] == "luna"
    assert lod[2]['dog'] == "stumpy"
    assert lod[3]['dog'] == "fido"

    assert lod[-1]['dog'] == "fido"
    assert lod[-2]['dog'] == "stumpy"
    assert lod[-3]['dog'] == "luna"
    assert lod[-4]['dog'] == "sunny"
    
    pass

def test_slicing_indexes():
    data = [{"dog": "sunny", "legs": 4}, 
            {"dog": "luna", "legs": 4}, 
            {"dog": "stumpy", "legs": 3}, 
            {"dog": "fido"}]
    lod = listofdicts.from_json(data)

    assert lod[0:2] == [{"dog": "sunny", "legs": 4}, {"dog": "luna", "legs": 4}]
    assert lod[1:3] == [{"dog": "luna", "legs": 4}, {"dog": "stumpy", "legs": 3}]
    assert lod[2:4] == [{"dog": "stumpy", "legs": 3}, {"dog": "fido"}]
    assert lod[3:5] == [{"dog": "fido"}]

    assert lod[-3:-1] == [{"dog": "luna", "legs": 4}, {"dog": "stumpy", "legs": 3}]
    assert lod[-2:-1] == [{"dog": "stumpy", "legs": 3}]
    assert lod[-1:] == [{"dog": "fido"}]

    pass

if __name__ == '__main__':
    test_slicing_indexes()