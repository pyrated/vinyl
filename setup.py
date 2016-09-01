from setuptools import setup, find_packages
import os
import vinyl


_REQUIRES = []

# We cannot install llvmlite on READTHEDOCS
if os.environ.get('READTHEDOCS') != 'True':
    _REQUIRES.append('llvmlite')

setup(name='vinylang',
      version=vinyl.__version__,
      author='Scott LaVigne',
      author_email='pyrated@gmail.com',
      url='https://github.com/pyrated/vinyl',
      license='Unlicense',
      description='The vinyl compiler',
      long_description=open('README.rst').read(),
      download_url='https://github.com/pyrated/vinyl.git',
      packages=find_packages(),
      requires=_REQUIRES,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.5'
      ])
