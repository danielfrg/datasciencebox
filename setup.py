from setuptools import setup, find_packages

'''
To update to a new version:
1. change version
2. python setup.py sdist register upload
'''

setup(name='datasciencebox',
      version='0.2',
      description='Data Science Box',
      long_description='',
      author='Daniel Rodriguez',
      author_email='df.rodriguez@gmail.com',
      url='https://github.com/danielfrg/datasciencebox',
      license='MIT',
      packages=find_packages(),
      entry_points='''
        [console_scripts]
        dsb=datasciencebox.cli.main:main
        datasciencebox=datasciencebox.cli.main:main
      ''',
      install_requires=[
        'click>=4.1',
        'Fabric>=1.10.2',
        'apache-libcloud>=0.17.0',
        'salt-ssh>=2015.5.3',
        'watchdog>=0.8.3',
    ]
)
