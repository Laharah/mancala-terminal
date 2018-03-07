from setuptools import setup
from setuptools.extension import Extension

ext_modules = [
    Extension('cstate',
              ['mancala/cstate.c'])
]

setup(
    name = 'Mancala',
    version= '0.1.0',
    url='',
    license='MIT',
    author='laharah',
    author_email='laharah22+mc@gmail.com',
    description='basic mancala game with bot',
    packages=['mancala'],
    ext_modules = ext_modules
)
