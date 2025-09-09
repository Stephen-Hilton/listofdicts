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


if __name__ == '__main__':
    # test_usage()
    test_negative_indexes()