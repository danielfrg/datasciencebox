# DataScienceBox

Command line utility to create instances in the cloud ready for data science.

## Installation

`git clone git@github.com:danielfrg/datasciencebox.git` and `pip install -e .`

## Usage

The basic usage is very similar to `vagrant`, `fabric` or `docker` in which you create a
`Vagrantfile`, `fabfile` or `Dockerfile` respectively and execute the command line
in the directory that contains that file.

In this case you create a `dsbfile` and use the `dsb` (or `datasciencebox`) command.


This makes it possible to version control everything, from box settings to custom salt states.

A `dsbfile` is a yaml file and looks like this:

```yaml
cloud: aws
region: us-east-1

image: ami-d6cf93be

size: m3.large
user: ubuntu
keyname: <EC2_KEYNAME>
keypair: ~/.ssh/<EC2_KEYPAIR>.pem

security_groups:
  - open

minion:
    number: 3
```

**Credentials**: You dont want credentials to be uploaded to the version control (trust me), so
`dsb` will also read a `dsbfile.secret` (that you can ignore in your vcs) in the same directory where you can have
for example your ec2 credentials.

```yaml
key: <KEY>
secret: <SECRET>
```

**Note**: No security groups or keypairs are created for you.

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
