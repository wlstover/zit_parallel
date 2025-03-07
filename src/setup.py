from setuptools import setup
from Cython.Build import cythonize

setup(
    name='ZIT Parallel',
    ext_modules = cythonize(["rng.pyx", "trades.pyx"]),
)