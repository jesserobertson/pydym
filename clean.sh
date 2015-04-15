python setup.py update_version
find . -name "__pycache__" | xargs rm -rf
rm -rf build dist *.egg-info
