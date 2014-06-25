#!/usr/bin/env bash
# file: install_deps.sh
# author: Jess Robertsob
#         CSIRO Minerals Resources Flagship
# date:   Wednesday 25 June 2014
#
# description: Install dependencies for pydym on Linux systems
#     THis script assumes you have MPI libraries, compilers and 
#     and autoconf tools available

# Access to source repositories on Bitbucket and Github
export GITHUB_PREFIX="git@github.com:jesserobertson"
export BITBUCKET_PREFIX="git@bitbucket.org:jessrobertson"

# Source code repositories
export PETSC_REPO="${BITBUCKET_PREFIX}/petsc.git"
export PETSC4PY_REPO="${BITBUCKET_PREFIX}/petsc4py.git"
export SLEPC_REPO="${BITBUCKET_PREFIX}/slepc.git"
export SLEPC4PY_REPO="${BITBUCKET_PREFIX}/slepc4py.git"
export MPI4PY_REPO="${BITBUCKET_PREFIX}/mpi4py.git"
export CYTHON_REPO="${GITHUB_PREFIX}/cython.git"

# Install locations
export BUILD_DIR="/media/stash/tmp/build"
export PREFIX="/home/jess/bin"
CURRENT_DIR = `pwd`

# Make sure we have a build directory available
if [[ -e ${BUILD_DIR} ]]; then
     mkdir -p ${BUILD_DIR}
fi

# Use aptitude for petsc
sudo aptitude install petsc-dev libslepc3.2-dev
export PETSC_ARCH="linux-gnu-c-opt"
export PETSC_DIR="/usr/lib/petscdir/3.2"
include /usr/lib/petscdir/3.2/linux-gnu-c-opt/conf/petscvariables

# Download and install Cython
cd ${BUILD_DIR}
git clone ${CYTHON_REPO}
cd cython
python setup.py install --user

# Download and install MPI4Py
cd ${BUILD_DIR}
git clone ${MPI4PY_REPO}
cd mpi4py
python setup.py install --user

# Download and install PETSc4Py
cd ${BUILD_DIR}
git clone ${PETSC4PY_REPO}
cd petsc4py
python setup.py install --user

# Download and install slepc4py
cd ${BUILD_DIR}
git clone ${SLEPC4PY_REPO}
cd slepc4py
python setup.py install --user
