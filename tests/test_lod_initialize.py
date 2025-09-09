from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts

def test_can_initialize():
    obj = listofdicts([{"key": "value"}])
    assert isinstance(obj, listofdicts)
 

if __name__ == '__main__':
    # test_usage()
    test_can_initialize()