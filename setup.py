from setuptools import setup, find_packages

import carton_flexible


setup(
    name='django-carton-fleixble',
    version=carton_flexible.__version__,
    description=carton_flexible.__doc__,
    packages=find_packages(),
    url='http://github.com/askholme/django-carton/',
    author='askholme',
    long_description=open('README.md').read(),
    include_package_data=True,
)
