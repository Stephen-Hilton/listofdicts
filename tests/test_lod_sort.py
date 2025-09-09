from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts
 

def test_sort():
    """
    sort() is a convenience function that sorts the listofdicts in-place by the specified key
    it can also be called with a keyname as a string, or a list of keynames
    """
    # test data
    lod = listofdicts()
    for i in range(1,101):
        lod.append({'order':i, 'randint':random.randint(1,100), 'randfloat':random.random()})
    assert len(lod) == 100

    # you can sort by any key that appears in all dicts
    lod.sort('randint')
    for keyname in ['randfloat', 'order', 'randint']:
        lod.sort(keyname)
        prev = 0
        for d in lod:
            assert d[keyname] >= prev # current should always he larger or equal to previous
            prev = d[keyname]
    
    # can also sort by multiple keys:
    lod.sort(['randint', 'randfloat'])
    prev = 0
    for d in lod:
        assert d['randint']*1000 + d['randfloat'] >= prev # current should always he larger or equal to previous
        prev = d['randint']*1000 + d['randfloat']

    pass



if __name__ == '__main__':
    # test_usage()
    test_sort()