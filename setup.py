from setuptools import setup, find_packages
import vinyl


args = dict()

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
      requires=open('requirements.txt').read().splitlines(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.5'
      ])
