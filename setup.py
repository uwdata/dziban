import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = os.path.abspath(os.path.dirname(__file__))

# From https://github.com/jupyterlab/jupyterlab/blob/master/setupbase.py, BSD licensed
def find_packages(top=HERE):
    """
    Find all of the packages.
    """
    packages = []
    for d, dirs, _ in os.walk(top, followlinks=True):
        if os.path.exists(os.path.join(d, '__init__.py')):
            packages.append(os.path.relpath(d, top).replace(os.path.sep, '.'))
        elif d != top:
            # Do not look for packages in subfolders if current is not a package
            dirs[:] = []
    return packages

PACKAGES = find_packages()

setup(
  name='dziban',
  version='0.0.1',
  packages=PACKAGES,
  license='BSD 3-Clause License',
  long_description=open('README.md').read(),
)