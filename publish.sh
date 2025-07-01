setop
echo "Remeber to update the version in the pyproject.toml file."
echo "You can do it now, if needed.  Press enter when ready."
read _ 

cd ~/Dev/listofdicts
rm -r dist src/*.egg-info
pip install --upgrade pip
python3 -m pip install "setuptools<68.0.0" wheel build twine
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade twine
python3 -m pip install --upgrade build
python3 -m build

# check before we upload:
twine check dist/*

# upload
twine upload -r pypi dist/*
# twine upload -r testpypi dist/*