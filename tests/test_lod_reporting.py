from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts
 

def test_str():

    # test data
    lod = listofdicts([{"cat": "zelda", "legs":4},
                       {"cat": "link", "legs":4},
                       {"cat": "stumpy", "legs":3}], append_only=True)
    assert isinstance(lod.__str__(), str) 

    cols = 2
    lines = len(lod) * cols        # rows * columns 
    lines += 1 + (len(lod)-1) + 1  # open + delimiters + close 
    lines += 2                     # Section headers for data + metadata 
    lines += 1                     # Metadata output
    assert len(lod.__str__().split("\n")) == lines

    lod.filter('cat', 'link') # 1 row
    lines = (len(lod) * (cols+1)) + 4  # expected lines
    assert len(lod.__str__().split("\n")) == lines
    
    lod = listofdicts([]) # 0 rows
    lines = (len(lod) * (cols+1)) + 4  # expected lines
    assert len(lod.__str__().split("\n")) == lines
    
    lod = listofdicts( [{'str':str(r), 'int':r} for r in range(0,100)] ) # 100 rows
    lines = (len(lod) * (cols+1)) + 4  # expected lines
    assert len(lod.__str__().split("\n")) == lines

    # all metadata is just stacked on one line
    for r in range(0,10):
        lod.metadata[f'test{r}'] = f'test{r}'
    assert len(lod.__str__().split("\n")) == lines

    pass 

 
if __name__ == '__main__':
    test_str()