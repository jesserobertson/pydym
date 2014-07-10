""" file:   setup.py (pydym)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday 1 May,
        2013

    description: Distutils installer script for cWavelets.
"""

from setuptools import setup, find_packages


## PACKAGE INFORMATION
setup(
    name='pydym',
    version='0.0.1',
    description='Dynamic mode decompositions of data in Python',
    author='Jess Robertson',
    author_email='jesse.robertson@csiro.au',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=[
        'h5py>=2.0.0',
        'matplotlib>=1.0.0',
        'numpy>=1.8.0',
        'scipy>=0.10.0',
    ],
    test_suite='tests',
    ext_modules=[],
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
        'Topic :: Scientific/Engineering :: Geology',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
