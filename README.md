# DataScienceBox

![travis-ci](https://travis-ci.org/danielfrg/datasciencebox.svg)

Command line utility to create instances in the cloud ready for data science.

## Installation

`pip install datasciencebox`

## Usage

The basic usage is very similar to `vagrant`, `fabric` or `docker` in which you create a
`Vagrantfile`, `fabfile` or `Dockerfile` respectively and execute the command line
in the directory that contains that file.

In this case you create a `dsbfile` and use the `dsb` (or `datasciencebox`) command.

This makes it possible to version control everything, from box settings to custom salt states.

A `dsbfile` is a python file and looks like this (for aws):

```python
CLOUD = 'aws'

AWS_KEY = '<KEY>'
AWS_SECRET = '<SECRET_KEY>'
AWS_REGION = 'us-east-1'
AWS_IMAGE = 'ami-d6cf93be'
AWS_SIZE = 'm3.large'
AWS_KEYNAME = '<EC2_KEYNAME>'
AWS_SECURITY_GROUPS = ['default']

USERNAME = 'ubuntu'
KEYPAIR = '~/.ssh/<EC2_KEYPAIR>.pem'
NUMBER_INSTANCES = 3
```

**Credentials**: You don't want credentials to be uploaded to the version control (trust me).
But since the `dsbfile` is a python file you can always do something like this
to read from environment variables for example:

```python
import os

AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']
```

**Note**: No security groups or keypairs are created for you its up to you to create
those in AWS.

### Creating the instances

Once the `dsbfile` is created you can create the instance(s) running `dsb up`.

This will create the instance(s) in the cloud provider and create a `.dsb` directory
in the same place as you `dsbfile`.

The `.dsb` directoy can be ignored for basic usage. It contains metadata about the instances
but it can also be used to controll the settings of the cluster and even upload new salt states.

###  Salt

[Salt](https://github.com/saltstack/salt) is the base for everything in `dsb`. Before running
anything you need to install the salt daemons on the instances and
sync the salt formulas to the salt master.

1. `dsb install salt`
2. `dsb sync`

Now you are ready to bootstrap stuff in you instances.

### Install miniconda

`dsb install miniconda` will install miniconda in all the instances.

#### conda packages

`dsb install conda <PKG_NAME>`, for example `dsb install conda numpy`

### Install OS packages

`dsb install pkg <PKG_NAME>`, for example `dsb install pkg build-essential`

### Jupyter Notebook

`dsb install notebook`, open the notebook URL by: `dsb open notebook`

### Spark

Spark is available via apache mesos, you need to bootstrap first hdfs and mesos.

1. `dsb install hdfs`: check that is running: `dsb open hdfs`
2. `dsb install mesos`: check that is running: `dsb open mesos`
3. `dsb install spark`

To test the easier way it to intall the Jupyter notebook and use use spark there,
note that if you already installed the notebook you have to run `dsb install notebook`
again.
