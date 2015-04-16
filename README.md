# pydym - Sparse and regular dynamic mode decompositions

Jess Robertson - @jesserobertson

[![Build Status](https://travis-ci.org/jesserobertson/pydym.svg?branch=develop)](https://travis-ci.org/jesserobertson/pydym) [![Code Health](https://landscape.io/github/jesserobertson/pydym/develop/landscape.svg?style=flat)](https://landscape.io/github/jesserobertson/pydym/develop)

_A library to calculate dynamic decompositions and sparse dynamic decompositions of physical system observations in Python. Runs in in Python 2.7 and 3.x._

## What's this all about then?



## Sounds great, how do I use it?

It's pretty straightforward to use - create snapshots (maybe from dumps from your simulation or experimentally using photographs/PIV/thermocouples insert your favourite tracking voodoo here), load them into a set of observations, and then pull out the modes:

```
import pydym

with pydym.load('simulations.hdf5') as data:
	results = dynamic_decomposition(data, burn=100)
	results.modes
```


### I need more details! How are you making that dataset in the first place?

The dataset is just a series of snapshots. A snapshot is just a list of positions, and a set of vector or scalar values observed at those positions. All the snapshots in a dataset should have the same position locations and the same properties. Note that you're not restricted to two dimensions - pydym can handle three dimensional data as well.

Here's an example of creating a Datum from the dumped output from a [Gerris](http://gfs.sourceforge.net) simulation. The first few lines of the dumped output looks like this:

```bash
cat dump_t15.dat
```

```
# 1:t 2:x 3:y 4:z 5:P 6:Pmac 7:U 8:V 9:T_x 10:T_y 11:T_alpha 12:T
15 -0.484375 -0.484375 0 -0.00989463 0.0405953 0 0 1 0 1 1
15 -0.453125 -0.484375 0 -0.0099109 0.0406551 3.41446e-05 -4.05764e-05 1 0 1 1
15 -0.421875 -0.484375 0 -0.00994345 0.0407747 9.81808e-05 -3.97415e-05 1 0 1 1
15 -0.390625 -0.484375 0 -0.0100156 0.0408324 9.81808e-05 -3.97415e-05 1 0 1 1
15 -0.359375 -0.484375 0 -0.0101274 0.0408284 0.000115172 -1.58028e-05 1 0 1 1
15 -0.328125 -0.484375 0 -0.0102562 0.0407457 0.000115172 -1.58028e-05 1 0 1 1
15 -0.296875 -0.484375 0 -0.010402 0.0405842 5.5562e-05 7.07383e-06 1 0 1 1
15 -0.265625 -0.484375 0 -0.0105522 0.0402551 5.5562e-05 7.07383e-06 1 0 1 1
```

You can easily create a Datum by slurping this into a numpy array and then pulling out the relevant columns to make a `pydym.Datum` object. 

```python
import pydym

def read_to_datum(filename):
	with open(filename, 'r') as fhandle:
		# Read in header
		regex = re.compile(r'.*:(.*)')
	    header = [regex.findall(k)[0]
	              for k in fhandle.readline().split()[1:]]

	    # Read in the rest of the file using numpy
	    data = numpy.loadtxt(fhandle)
	    snapshot = {h: data[:, header.index(h)] for h in header}
	    return pydym.Datum(
	        position=numpy.vstack([snapshot['x'], snapshot['y']]),
	        velocity=numpy.vstack([snapshot['U'], snapshot['V']]),
	        pressure=snapshot['P'],
	        tracer=snapshot['T'])

datum = read_to_datum('dump_t15.dat')
``` 

Note that we only need to have the position argument; all of the other keyword arguments are assumed to be observations for each of the positions. These are then available as arrays from the datum object

```python
print(datum.velocity)
# something
print(datum.pressure)
# something
```

Use Observations to store a set of snapshots. We use the excellent [h5py](http://h5py.org) library to provide on-disk storage which is transparent to you.

```python
files = ['dump_t0.dat', 'dump_t1.dat', ...]

data = pydym.Observations(
    filename='simulations.hdf5',
    scalar_datasets=('pressure', 'tracer'),
    n_snapshots=len(files),
    n_samples=len(datum))

for i, f in enumerate(files):
	data[i] = read_to_datum(f)
```

Having generated the backing file once, you can reload the data directly from the backing file:

```python
data = pydym.Observations('simulations.hdf5')
```

You can also load the simulation files directly using h5py if you want. Each vector is available as an HDF5 group where each dimension forms a dataset within that group (so to get the x component of velocity you'd get `data['velocity/x']`), while each scalar is available as a dataset directly (so you'd do something like `data['pressure']` for example). That's what we're doing above.

You need to clean up the hdf5 file references once you're done with them however, using `data.close()` or `del data`. We provide a 'load' function so you can load the file in a nice `with` environment which does the file handling for you once you exit the `with` context:

```python
with pydym.load('simualtions.hdf5') as data:
	u = data['velocity/x']
	# do something with data here

# Python cleans up all your hdf5 file references for you here
```

## Install

Requirements are in `requirements.txt`: numpy, scipy, matplotlib and h5py. Easiest install uses [Anaconda](https://store.continuum.io/cshop/anaconda/) binaries:

```bash
# cd to-source-directory
conda install --file requirements.txt
```

Then the rest of the library can be installed from source:

```bash
python setup.py install
```

To check that the install works ok, you can run the test suite as well: `python run_test.py`.
