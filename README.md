# DataScienceBox

[![travis-ci](https://travis-ci.org/danielfrg/datasciencebox.svg)](https://travis-ci.org/danielfrg/datasciencebox)

Command line utility to create instances in the cloud ready for data science.
Includes conda package management plus some Big Data frameworks (spark).

## Installation

`pip install datasciencebox`

## Usage

The basic usage is very similar to `vagrant`, `fabric` or `docker` in which you create a
`Vagrantfile`, `fabfile` or `Dockerfile` respectively and execute the command line
in the directory that contains that file.

In this case you create a `dsbfile` and use the `dsb` (or `datasciencebox`) command.

This makes it possible to version control everything, from box settings to custom salt states.

A `dsbfile` is a python file and looks like this:

```python
# AWS
CLOUD = 'aws'

AWS_KEY = '<KEY>'
AWS_SECRET = '<SECRET_KEY>'
AWS_REGION = 'us-east-1'
AWS_IMAGE = 'ami-d6cf93be'
AWS_SIZE = 'm3.large'
AWS_KEYNAME = '<EC2_KEYNAME>'
AWS_SECURITY_GROUPS = ['default']

# ALL
USERNAME = 'ubuntu'
KEYPAIR = '~/.ssh/<EC2_KEYPAIR>.pem'
NUMBER_INSTANCES = 3
```

**Supported OS**: At this moment only Ubuntu (12.04 and 14.04) are supported.

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
there are two ways of bootstraping stuff into the nodes,
salt master (via ZMQ - recommended) or salt ssh.

The recommended way is using salt via ZMQ which requires the salt master
and minion to be installed in the nodes you can install by running this:

``` bash
$ dsb install salt
```

This is the default and recommended behavior but you can use salt-ssh and not
install anything in your nodes while getting the same results (in most cases)
by adding a `--ssh` flag to all the commands.
Note that this works well for some commands like `install conda` and `install pkg`
but might not works as expected for the distributed frameworks like zookeeper and mesos.

## General management

### Install OS packages

```bash
$ dsb install pkg <PKG_NAME>
$ # Example
$ dsb install pkg build-essential
$ dsb install pkg build-essential --ssh
```

## Conda management

Conda package management is done for the `dsb` user in all the nodes.

You need to install miniconda in all the nodes:

```bash
$ dsb install miniconda
$ dsb install miniconda --shh
```

### conda packages

```bash
$ dsb install conda <PKG_NAME>
$ # Example
$ dsb install conda numpy
$ dsb install conda numpy --ssh
```

### Jupyter Notebook

```bash
$ dsb install notebook
$ dsb open notebook
```

## Cloudera

### HDFS

```bash
$ dsb install hdfs
$ dsb open hdfs
```

## Mesos

```bash
$ dsb install mesos
$ dsb open mesos
```

### Spark

Spark is available usint  mesos as scheduler, hdfs is also required.

```bash
$ dsb install spark
```

To test the easier way it to intall the Jupyter notebook and use use spark there,
note that if you already installed the notebook you have to run `dsb install notebook`
again.

### Marathon

Marathon can be used to deploy any application or docker container in Mesos.

```bash
$ dsb install mesos-marathon
$ dsb open mesos-marathon
```
