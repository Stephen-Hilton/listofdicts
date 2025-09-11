from pathlib import Path
import pytest, random, json, sys, string
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts



def test_pops():
    lod = listofdicts()
    for i in range(50):
        lod.append( {'size': random.choice(['giant','big','medium','small','toy']),
                      'id': random.randint(100000,999999),
                      'code': random.randint(1,3) } )
    # to avoid false-negatives during testing:
    lod.append( {'size': 'giant',
                 'id': random.randint(100000, 999999),
                 'code': random.randint(1, 3) } )
    lod.append( {'size': 'toy',
                 'id': random.randint(100000, 999999),
                 'code': random.randint(1, 3) } )
    lod.append( {'size': 'medium',
                 'id': random.randint(100000, 999999),
                 'code': 3 } )
    
    # create dups in both 'toy' and 'giant'
    lod = lod + [d for d in lod if d['size'] in ['toy','giant']]
    
    # define a way to get dups:
    def getdups(lod):
        rtn = []
        prev = {}
        for idx, itm in enumerate(lod): # this preserves the filter settings
            if itm == prev: # dup found
                rtn.append( {'id':itm['id'], 'index':idx} )
            prev = itm
        return rtn

    # let's look at just our toys:
    print(lod.filter('size', 'toy').sort('id'))

    dups = getdups(lod) # because it's filtered, this returns just 'toy' dups
    print(dups)
    assert len(dups) > 0

    # dedup with pop() -- needs to be reversed / big-to-small,
    # otherwise we change index of bigger indexes when we remove smaller indexes
    for d in reversed(dups):
        popped_dict = lod.pop(d['index']) # this returns the data dict
        assert popped_dict['id'] == d['id'] # should match
        assert popped_dict['size'] == 'toy' # still filtered
        
    # now that we're deduped, let's check again:
    dups = getdups(lod)
    assert len(dups) == 0

    # Above was on a filtered subset of the LoD, so it did not dedup entire dataset
    # i.e., how many dups do we have for our giants?
    print(lod.filter('size', 'giant').sort('id'))
    
    dups = getdups(lod) # because it's filtered, this returns just 'toy' dups
    print(dups)
    assert len(dups) > 0

    # rather than dedup manually, you can also use the uniquify() function:
    lod.uniquify()  

    dups = getdups(lod)
    assert len(dups) == 0
    

    # let's get rid of any code 3 medium records, using del:
    lod.filter('size', 'medium').sort(['code','id'])
    print(lod)
    code3 = len([d for d in lod if d['code']==3])
    assert code3 > 0

    # find the index positions:
    delindexes = []
    for i, d in enumerate(lod):
        if d['code'] == 3: delindexes.append(i)
    
    # execute the del 
    for i in reversed(delindexes): del lod[i]

    # check it worked:
    for d in lod:
        assert d['code'] != 3
    
    return None
    # TODO: make this work the way it reads:
    lod.filter('size', 'giant').filter('code', 3)
    # or 
    lod.filter('size', 'giant').filter('code', 3)


 



if __name__ == '__main__':
    test_pops()