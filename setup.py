from distutils.core import setup
from setuptools import find_packages
# from setuptools import setup, find_packages

"""
To upload a new version:
0. rm -rf *.egg-info
1. change version
2. python setup.py sdist register upload
"""
print(find_packages())
setup(name='datasciencebox',
      version='0.3',
      description='Data Science Box',
      long_description='',
      author='Daniel Rodriguez',
      author_email='df.rodriguez@gmail.com',
      url='https://github.com/danielfrg/datasciencebox',
      license='Apache 2.0',
      packages=find_packages(),
      include_package_data=True,
      entry_points="""
        [console_scripts]
        dsb=datasciencebox.cli.main:start
        datasciencebox=datasciencebox.cli.main:start
      """,
      install_requires=[
        'click>=4.1',
        'Fabric>=1.10.2',
        'apache-libcloud>=0.17.0',
        'salt-ssh>=2015.5.3',
        'watchdog>=0.8.3',
    ]
)
