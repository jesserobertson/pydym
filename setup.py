""" file:   setup.py (pydym)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday 1 May,
        2013

    description: Distutils installer script for cWavelets.
"""

from setuptools import setup, find_packages

# Get requirements from requirements.txt file
with open('requirements.txt') as fhandle:
    REQUIREMENTS = [l.strip('\n') for l in fhandle]

# Get version number from _version.py
# Can be updated using python setup.py update_version
from update_version import update_version, Version, get_version
update_version()

## PACKAGE INFORMATION
setup(
    # Metadata
    name='pydym',
    version=get_version(),
    description='Sparse and regular dynamic mode decomposition (DMD) of observations of physical systems',
    author='Jess Robertson',
    author_email='jesse.robertson@csiro.au',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # Requirements
    install_requires=[
        'h5py>=2.0.0',
        'matplotlib>=1.0.0',
        'numpy>=1.8.0',
        'scipy>=0.10.0'
    ],

    # Contents
    packages=find_packages(exclude=['tests', 'docs']),
    test_suite='tests',
    ext_modules=[],
    cmdclass={
        'update_version': Version,
    }
)
