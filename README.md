# pydym
_Sparse and regular dynamic mode decompositions (DMD) of physical system observations in Python (2.7 and 3.x.)_

Jess Robertson - @jesserobertson (twitter & github)

[![Build Status](https://travis-ci.org/jesserobertson/pydym.svg?branch=develop)](https://travis-ci.org/jesserobertson/pydym) [![Code Health](https://landscape.io/github/jesserobertson/pydym/develop/landscape.svg?style=flat)](https://landscape.io/github/jesserobertson/pydym/develop)

## What's this all about then?

As a general rule, interesting physical systems have complex dynamics. We'd like to be able to describe these dynamics in terms of a (preferrably small number) of processes which drive the dynamics, either directly or via process interactions. Dynamic mode decomposition is part of a family of methods for pulling out these simpler low-order models from observations of a physical system (e.g. photographs/PIV/PTV, experimental measurements or simulation outputs) without having to have access to the complete set of equations that define the system dynamics (Schmid, 2010). DMD instead uses successive time-stepped snapshots to invert for the essential features of a system that can be used to construct a low-order approximation.

Generally DMD gives you back a lot of modes. You can use these to reconstruct the system dynamics completely. But sometimes it's nice to be able to say which of these modes we need to best approximate the system dynamics without having to use all of them. The sparsity preserving dynamic mode decomposition (DMDsp) of Jovanovic et al. (2014) uses a aumented Lagrangian approach to optimize the number of modes returned to best approximate the system dynamics. So you can effectively place limits on how good you want the approximation to be and the DMDsp algorithm will give you the optimal number of modes to generate that approximation.

Here's a couple of useful references with all the gory details:

- Schmid, P. J. (2010) Dynamic mode decomposition of numerical and experimental data. _Journal of Fluid Mechanics_ **656**, doi: [10.1017/S0022112010001217](http://dx.doi.org/10.1017/S0022112010001217)
- Jovanovic, M. R., Schmid, P. J. & Nichols, J. W. (2014) Sparsity-promoting dynamic
mode decomposition. _Physics of Fluids_ **26**, doi: [10.1063/1.4863670](http://dx.doi.org/10.1063/1.4863670) ([also available here](http://www.ece.umn.edu/users/mihailo/papers/jovschnicPOF14.pdf))

Mihailo Jovanovic also provides MATLAB code for doing this on his [personal website](http://www.ece.umn.edu/users/mihailo/software/dmdsp/) if you'd rather use MATLAB. His site also has a much nicer description of the DMDsp approach that I give here. I just wanted a Python implementation that plays nicely with the numpy/scipy ecosystem and was backed by HDF5 for data storage.

## Sounds great, how do I use it?

It's pretty straightforward to use - create snapshots (maybe from dumps from your simulation or experimentally using photographs/PIV/thermocouples insert your favourite tracking voodoo here), load them into a set of observations, and then pull out the modes:

```python
import pydym

with pydym.load('simulations.hdf5') as data:
	results = pydym.dynamic_decomposition(data)
	print(results.modes)
# prints: <HDF5 group "/modes/" (500 members)>
```

Note that you'll get back as many modes as you have snapshots (less one). That might be a lot to trawl through so it's nice to approximate this in some way with a lower number of modes that capture _most_ of the dynamics of your system. That's where the sparsity-enforcing algorithm of Jovanovic et al. (2014) comes in.

You can enforce the sparsity by chaining on the sparsify function

```python
with pydym.load('simulations.hdf5') as data:
	sparse_results = pydym.dynamic_decomposition(data).sparsify(0.1)
	print(len(sparse_results.modes))
# prints: 3
```

### I need more details! How are you making that observations dataset in the first place?

The dataset is just a series of snapshots. A snapshot is just a list of positions, and a set of vector or scalar values observed at those positions. All the snapshots in a dataset should have the same position locations and the same properties. Note that you're not restricted to two dimensions - pydym can handle three dimensional data as well.

Here's an example of creating a Snapshot from the dumped output from a [Gerris](http://gfs.sourceforge.net) simulation. The first few lines of the dumped output looks like this:

```
$ head dump_t15.dat

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

You can easily create a Snapshot by slurping this into a numpy array and then pulling out the relevant columns to make a `pydym.Snapshot` object. Here's how we might wrap that into a function to read the data from a file and return a `Snapshot`.

```python
def read_to_snapshot(filename):
	""" Create a snapshot from a Gerris file dump

		Parameters: 
			filename - the location of the Gerris output file

		Returns:
			a pydym.Snapshot object containing the observational data
	"""
	with open(filename, 'r') as fhandle:
		# Read in header
		regex = re.compile(r'.*:(.*)')
	    header = [regex.findall(k)[0]
	              for k in fhandle.readline().split()[1:]]

	    # Read in the rest of the file using numpy
	    data = numpy.loadtxt(fhandle)
	    data_columns = {h: data[:, header.index(h)] for h in header}
        snapshot = Snapshot(
            position=numpy.vstack([data_columns['x'], data_columns['y']]),
            velocity=numpy.vstack([data_columns['U'], data_columns['V']]),
            pressure=data_columns['P'],
            tracer=data_columns['T'])
        return snapshot
```

and now we can do something like:

```python
snap = read_to_snapshot('dump_t15.dat')
``` 

Note that we only need to have the position argument; all of the other keyword arguments are assumed to be observations for each of the positions. These are then available as arrays from the `pydym.Snapshot` object:

```python
print(snap.velocity)
# prints: [[0.1242563 0.1342345 ... ] [0.2541345 0.2341342 ... ]]
print(snap.pressure)
# prints: [1.4256323  2.314562 ... ]
```

### But I'll have more than one snapshot...

Use Observations to store a set of snapshots. We use the excellent [h5py](http://h5py.org) library to provide on-disk storage which is transparent to you.

```python
files = ['dump_t0.dat', 'dump_t1.dat', ...]

observ = pydym.Observations(
    filename='simulations.hdf5',
    scalar_datasets=('pressure', 'tracer'),
    n_snapshots=len(files),
    n_samples=len(Snapshot))

for i, f in enumerate(files):
	observ[i] = read_to_snapshot(f)
```

You can then pull out the Snapshots as if they were sitting in a list:

```python
print(observ[0])
# prints: <pydym.snapshot.Snapshot at 0x1054b01d0>
```

Having generated the backing file once, you can reload the data directly from the backing file:

```python
del observ
observ = pydym.Observations('simulations.hdf5')
print(observ[0])
# prints: <pydym.snapshot.Snapshot at 0x1054b02e8>
```

You can also load the simulation files directly using h5py if you want. Each vector is available as an HDF5 group where each dimension forms a dataset within that group (so to get the x component of velocity you'd get `data['velocity/x']`), while each scalar is available as a dataset directly (so you'd do something like `data['pressure']` for example). 

You need to clean up the hdf5 file references once you're done with them however, using `data.close()` or `del data`. If you don't do this then your hdf5 file might be left in a strange state and refuse to load later on. We provide a 'load' function so you can load the file in a nice `with` environment which does the file handling for you once you exit the `with` context:

```python
with pydym.load('simualtions.hdf5') as data:
	u = data['velocity/x']
	# do something with data here

# Python cleans up all your hdf5 file references for you here
```

That's what we're doing above.

If you come up with a nice function to import data from your simulation output format of choice, feel free to stick it in the pydym.io module and submit a pull request.

## Where can I get it?

Requirements are in `requirements.txt`: numpy, scipy, matplotlib and h5py. Easiest install uses [Anaconda](https://store.continuum.io/cshop/anaconda/) binaries:

```bash
# cd to-source-directory
conda install --file requirements.txt
```

Then the rest of the library can be installed from source:

```bash
python setup.py install
```

To check that the install works ok, you can run the test suite as well: `python run_test.py`. We have automated unit testing and lint checks for the repository as well - just click on the little icons above to go to TravisCI and landscape.io.

One of these days I'll get around to putting a package up on pypi or binstar...
