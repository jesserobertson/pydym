find . -name "__pycache__" | xargs rm -r
rm -rf build dist *.egg-info
python setup.py update_version
