from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("rng", ["rng.pyx"], extra_compile_args=["-std=c99"]),
    Extension("main", ["main.pyx"], extra_compile_args=["-std=c99"]),
    Extension("data", ["data.pyx"], extra_compile_args=["-std=c99"]),
]

setup(
    ext_modules=cythonize(extensions))
