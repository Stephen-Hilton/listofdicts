from pathlib import Path
import pytest, random, json, sys

lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts


def test_uniquify():
    # test data
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4},
                       {"legs":4, "cat": "link"}
                       ] )
    
    # by default, duplicates are fine:
    assert len(lod) == 6
    
    # but you may want a unique set. This will remove records (not a filter), regardless of key order.
    lod.uniquify()
    assert len(lod) == 3

    # you can use it in conjunction with a filter:
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "zelda", "legs":4},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "stumpy", "legs":3},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "link", "legs":4}
                       ] )
    
    # just uniquify the "link" cat, leaving "stumpy" dups:
    lod.filter("cat", "link").uniquify()
    assert len(lod.clear_filter()) == 6 # zelda x2, stumpy x3, link x1 (dedup'd)

    # or you can uniquify all of dicts:
    lod.clear_filter().uniquify()
    assert len(lod.clear_filter()) == 3 # zelda x1, stumpy x1, link x1 (dedup'd)



if __name__ == '__main__':
    test_uniquify()