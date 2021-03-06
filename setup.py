# coding=utf-8

"""
Set up packaging, unit tests and dependencies.
"""

from setuptools import find_packages, setup

setup(
    name='genview',
    version='0.3.0',

    author='Radoslav Klic',
    description='Simple test environment for Geneea generator',
    keywords='natural language generation',
    url='https://geneea.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License'
    ],

    # Dependencies
    install_requires=[
        'Jinja2>=2.10', 'starlette>=0.13', 'aiohttp>=3.6', 'uvicorn>=0.11', 'python-multipart>=0.0.5', 'ujson>=2.0'
    ],


    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),

    package_data={
        'genview.templates': ['*.html']
    },

    test_suite='genview'
)
