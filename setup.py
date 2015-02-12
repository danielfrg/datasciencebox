try:
    from setuptools import setup
except:
    from distutils.core import setup

'''
To update to a new version:
1. change version
2. python setup.py sdist register upload
'''

setup(name='datasciencebox',
      version='0.0.1',
      description='Data Science Box',
      long_description='',
      author='Daniel Rodriguez',
      author_email='df.rodriguez@gmail.com',
      url='https://github.com/danielfrg/datasciencebox',
      license='LICENSE.txt',
      namespace_packages = [
        'datasciencebox'
      ],
      packages=[
          'datasciencebox.cli',
          'datasciencebox.core'
      ],
      entry_points='''
        [console_scripts]
        dsb=datasciencebox.cli.cli:main
        datasciencebox=datasciencebox.cli.cli:main
      ''',
      install_requires=[
        'click>=3.3',
        'Fabric>=1.10.1',
        'apache-libcloud>=0.16.0',
        'salt-ssh>=2014.7.1',
        'watchdog>=0.8.3',
    ]
)
