# DataScienceBox

Command line utility to create instances in the cloud ready for data science.

## Installation

`git clone git@github.com:danielfrg/datasciencebox.git` and `pip install -e .`

## Usage

CLI is available as `datasciencebox` or `dsb`

Run `dsb` once to create the directories, all settings are located in `~/.datasciencebox`:

1. `~/.datasciencebox/clusters`: running cluster information
1. `~/.datasciencebox/profiles`: profiles have instance information
1. `~/.datasciencebox/providers`: providers have login information on cloud providers

### 1. Create provider

`~/.datasciencebox/providers/aws.yaml`

```
aws:
  cloud: aws
  region: us-east-1
  key: XXXXXXXXXXXXXXX
  secret: XXXXXXXXXXXXXXX
```

### 2. Create profiles

`~/.datasciencebox/providers/small.yaml`

```
small:
  provider: aws
  size: t1.micro
  image: ami-daaed0b2
  user: ubuntu
  keyname: my_key
  keypair: ~/.ssh/my_key.pem
  security_groups:
    - open
  minions:
    n: 2
```

### 3. Create instances

`dsb create new_cluster`

New instances will be created and a `~/.datasciencebox/cluster/new_cluster` directory
will be created will the cluster information and settings.

## Packages

Before doing anything else we need to install salt in the instances

`dsb install salt` will bootstrap salt-master and salt-minion using salt-ssh

`dsb rsync --once` will sync salt formulas and pillar settings (see Configuration below)

### miniconda

`dsb install miniconda` will bootstrap (mini)conda in all the instances

After its installed conda (and pypi) packages can be installed using `dsb install conda`

### conda

Requires: miniconda

`dsb install conda requests` will install requests in all the instances (master + minion)

`dsb install conda numpy '*minion*'` will install numpy in all the minions

### pip

Requires: miniconda

`dsb install pip boto` will install boto in all the instances

`dsb install pip boto '*'` will install boto in all the minions

### spark + HDFS

Note: Spark is supported via mesos

1. Install hdfs and mesos: `dsb install hdfs` and `dsb install mesos`
2. Install spark: `dsb install spark`

## Configuration

DataScienceBox is based on [salt](http://docs.saltstack.com/en/latest/)
so in order to change the settings of the instances you have to change the pillars located at
`~/.datasciencebox/cluster/{{ CLUSTER_NAME }}/pillar`. Default values will be located there.

After changing those values need to sync the pillars to the cluster: `dsb rsync --once`

## This is hard, it sucks!

This was started as a toy project and is my personal playground.
If you want a more complete product with MapReduce, Hive, Impala and more
with better support check out the spiritual succesor:
[conda-cluster](http://continuum.io/anaconda-cluster).
