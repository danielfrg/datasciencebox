from distutils.core import setup
from setuptools import find_packages

import versioneer

"""
To upload a new version:
0. rm -rf *.egg-info
1. change version
2. python setup.py sdist register upload
"""

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='datasciencebox',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
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
      install_requires=required)
