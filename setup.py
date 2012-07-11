import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from setuptools import setup

setup(
    name='axiom reqs',
    version='0.1',
    author='Axiom',
    author_email = '',
    description = 'Axiom Requirements HTML Outputter',
    license = 'MIT',
    py_modules = ['reqs'],
    entry_points = {
        'nose.plugins': [
            'reqs = reqs:ReqsOutput'
            ]
        }

    )