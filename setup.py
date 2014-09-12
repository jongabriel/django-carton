from setuptools import setup, find_packages

import carton


setup(
    name='django-carton',
    version=carton.__version__,
    description='Session only cart',
    packages=find_packages(),
    url='http://github.com/jongabriel/django-carton/',
    author='jongabriel',
    long_description=open('README.md').read(),
    include_package_data=True,
)
