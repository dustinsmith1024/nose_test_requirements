import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from setuptools import setup

setup(
    name='nose test requirements',
    version='0.1',
    author='Axiom',
    author_email = '',
    description = 'Nose plugin that outputs requirements in HTML',
    license = 'MIT',
    py_modules = ['plugin'],
    entry_points = {
        'nose.plugins': [
            'requirements = plugin:ReqsOutput'
            ]
        }

    )