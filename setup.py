#!/usr/bin/env python
from setuptools import setup

setup(
    name='django-randomfilenamestorage',
    version='1.0',
    description=('A Django storage backend that gives random names to files.'),
    author='Akoha Inc.',
    author_email='adminmail@akoha.com',
    url='http://bitbucket.org/akoha/django-randomfilenamestorage/',
    packages=['django_randomfilenamestorage'],
    package_dir={
        'django_randomfilenamestorage': 'django_randomfilenamestorage'
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=True,
)
