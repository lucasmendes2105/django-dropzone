import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dropzone',
    version='0.5.1',
    packages=['dropzone'],
    include_package_data=True,
    license='MIT License',  # example license
    description='Dropzone is a Django app that facilitates integration with Django Admin and Dropzone.js',
    long_description=README,
    url='http://www.virtualizei.com/',
    author='Lucas Mendes',
    author_email='lucasmendes2105@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
