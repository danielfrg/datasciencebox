# DataScienceBox

[![travis-ci](https://travis-ci.org/danielfrg/datasciencebox.svg)](https://travis-ci.org/danielfrg/datasciencebox)

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

## Creating the instances

Once the `dsbfile` is created you can create the instance(s) running `dsb up`.

This will create the instance(s) in the cloud provider and create a `.dsb` directory
in the same place as you `dsbfile`.

The `.dsb` directoy can be ignored for basic usage. It contains metadata about the instances
but it can also be used to control the settings of the cluster (pillars) and even upload custom salt states. This also allows to version control all the deployment of a cluster.

## Installing

Everyting in DSB is based on [Salt](https://github.com/saltstack/salt) and
there is two ways of bootstraping stuff into the nodes,
salt via ZMQ (recommended) or salt ssh.

The recommended way is using salt via ZMQ which requires the salt master
and minion to be installed in the nodes you can install by running this:

1. `dsb install salt`
2. `dsb sync`

This is the default and recommended behaviour but you can use salt-ssh and not
install anything in your nodes while getting the same results (in most cases)
by adding a `--ssh` flag to all the install commands.
Note that this works well for some commands like `install conda` and `install pkg`
but might not works as expected for the distributed frameworks like zookeeper and mesos.

### Install miniconda

Install miniconda under the `dsb` user

`dsb install miniconda` or `dsb install miniconda --shh`

### Install conda packages

`dsb install conda <PKG_NAME>`, for example `dsb install conda numpy` or
`dsb install conda numpy --ssh`

### Install OS packages

`dsb install pkg <PKG_NAME>`, for example `dsb install pkg build-essential` or
`dsb install pkg build-essential --ssh`

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
