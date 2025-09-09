from pathlib import Path
import pytest, random, json, sys
lodpath = Path(Path(__file__).parent.parent / 'src' / 'listofdicts')
sys.path.append( str(lodpath.resolve()) )
from listofdicts import listofdicts
 

def test_integrations():
    # pydantic:
    from pydantic import BaseModel 

    class Dog(BaseModel):
        name: str
        age: int
        limbs: listofdicts

    sparky = Dog(
        name='Sparky',
        age=3,
        limbs=listofdicts([
            {'name':'front left', 'length':10},
            {'name':'front right', 'length':10},
            {'name':'back left', 'length':10},
            {'name':'back right', 'length':10} ])
        )
    assert isinstance(sparky.limbs, listofdicts)    



if __name__ == '__main__':
    # test_usage()
    test_integrations()