from pathlib import Path
import pytest, random, json, sys

lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts


def test_lowify():
    # test data
    lod = listofdicts([ #           old -> new    old -> new   old -> new
                       {"Test": 1, "cat": "cat", "CaT":"CaT", "cAt":"cAt"},
                       {"Test": 2, "CAT": "CAT", "cat":"cat", "caT":"caT"},
                       {"Test": 3, "CaT": "cat", "cAt":"cAt", "cAT":"cAT"},
                       {"Test": 4, "CaT": "CaT", "Cat":"Cat", 'cat':'cat'},
                       ] )
    lod.lowify(include_only_keys=['Test'])
    for i,r in enumerate(lod):
        for k,v in r.items():
            if isinstance(v,int): 
                assert k == 'test'
                continue

    lod.lowify(keys=True, values=False)
    for i,r in enumerate(lod):
        for k,v in r.items():
            if k == 'test': continue
            print(f'row {i}: {k} -> {v}')
            assert v == k
        
    lod.lowify(keys=False, values=True)
    for i,r in enumerate(lod):
        for k,v in r.items():
            if k == 'test': continue
            assert v == 'cat'
            

    lod = listofdicts([{"Kid": "Susie", "Favorite Color": "Blue" , "Candy": "Ice Cream"},
                       {"Kid": "Joe",   "Favorite Color": "Green", "Candy": "Ice Cream"}])


    lod.lowify(keys=True, values=True, include_only_keys=[k for k in lod.unique_keys() if k != 'Kid' ] ) 
    assert lod == [{"Kid": "Susie", "favorite color": "blue" , "candy": "ice cream"},
                   {"Kid": "Joe",   "favorite color": "green", "candy": "ice cream"}]   

    lod.lowify(keys=True, values=False) 
    assert lod == [{"kid": "Susie", "favorite color": "blue" , "candy": "ice cream"},
                   {"kid": "Joe",   "favorite color": "green", "candy": "ice cream"}]   



if __name__ == '__main__':
    # test_usage()
    test_lowify()