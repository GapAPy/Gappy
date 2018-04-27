from setuptools import setup
from os import path
import sys
import re

here = path.abspath(path.dirname(__file__))

install_requires = ['requests>=2.18']

# Parse version
with open(path.join(here, 'gappy', '__init__.py')) as f:
    m = re.search('^__version_info__ *= *\(([0-9]+), *([0-9]+)\)', f.read(), re.MULTILINE)
    version = '.'.join(m.groups())


setup(
    
    name='gappy',
    packages=['gappy'],
    author = "Sadegh Yazdani, Hossein Hafarzade, Mostafa Asadi",
    author_email = "m.s.yazdani86@gmail.com",
    project_urls={
        "Source Code": "https://github.com/hsin75/Gappy",
    },
    install_requires=install_requires,

    version=version,

    description='Python framework for Gap Service API',

    long_description='',

    url='https://github.com/hsin75/Gappy',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='gap messenger bot api python wrapper',
)
