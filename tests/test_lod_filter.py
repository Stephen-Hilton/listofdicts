from pathlib import Path
import pytest, random, json, sys

lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts


def test_filter():
    # test data
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "link", "legs":4}
                       ] )
    
    # filter() dynamically limits data returned
    assert len(lod) == 3
    lod.filter("legs", 4) 
    assert len(lod) == 2
    
    i=0
    for cat in lod:
        assert cat["legs"] == 4
        i += 1
    assert i == 2
    
    # filter is active until cleared 
    assert len(lod) == 2
    assert lod[0]['cat'] == "zelda"
    assert lod[1]['cat'] == "link" 
    with pytest.raises(KeyError): lod[2]['cat'] == "stumpy" # out of bounds
    
    # data is just held back, not lost:
    lod.clear_filter()
    assert len(lod) == 3
    assert lod[1]['cat'] == "stumpy"

    # you can also assign names to filters:
    lod.filter("legs", 3, filter_name="3 legged") # assign name to filter when creating
    assert len(lod) == 1 
    lod.clear_filter() # full dataset again
    assert len(lod) == 3
    lod.filter(filter_name="3 legged") # reapply the same filter, by name (not re-defined)
    assert len(lod) == 1

    # Take care, the indexes will change to represent the filtered state:
    lod.filter("legs", 4, "typical cats")
    assert len(lod) == 2
    assert lod[0]["cat"] == "zelda"   
    assert lod[1]["cat"] == "link"    # link = index 1 

    lod.clear_filter()
    assert lod[0]["cat"] == "zelda"   
    assert lod[1]["cat"] == "stumpy"  
    assert lod[2]["cat"] == "link"    # link = index 2


    # this is also dynamic -- changing underlying data will immediately change the filtered result:
    lod.filter(filter_name = "typical cats")
    assert len(lod) == 2
    lod[1]["legs"] = 3   # change legs from 4 to 3
    assert len(lod) == 1 # filter is applied dynamically, no action required 

    lod.filter("legs", 3, filter_name="3 legged")
    assert len(lod) == 2
    lod[1]["legs"] = 4 # change legs back to 4
    assert len(lod) == 1

    # The KeyError ties to be helpful during out-of-bound indexes:
    # KeyError: 'Index 2 not found - filter active: "3 legged" which may be constraining data, try:  lod.clear_filter()'
    # Another reason to name filters (and clear them)

    # few other items of note:

    # you can also iterate directly from the filter object:
    for cat in lod.filter("legs", 4):
        assert cat["legs"] == 4
    
    assert len(lod) == 2  # although this still preserves the filtered state:
    
    # you can also clear the filter by calling filter() with no params:
    lod.filter()
    assert len(lod) == 3



if __name__ == '__main__':
    # test_usage()
    test_filter()