from setuptools import setup, find_packages
from os import path
import re

here = path.abspath(path.dirname(__file__))

install_requires = ['requests>=2.18']

# Parse version
with open(path.join(here, 'gappy', '__init__.py')) as f:
    m = re.search(
        '^__version_info__ *= *\(([0-9]+), *([0-9]+), *([0-9]+)\)',
        f.read(), re.MULTILINE)
    print(m)
    version = '.'.join(m.groups())


setup(
    name='gappy',
    author="Sadegh Yazdani, Hossein Jafarzadeh, Mostafa Asadi",
    author_email="m.s.yazdani86@gmail.com",
    project_urls={
        "Source Code": "https://github.com/GapAPy/Gappy/",
    },
    install_requires=install_requires,
    packages=find_packages(),
    version=version,

    description='Python framework for Gap Service API',
    long_description="""### Install Package
```
pip3 install gappy
```
compatible python version: 3.4+

### How to use

#### Run with flask

Example:

```
import gappy
from flask import Flask
from flask import request

TOKEN = '<your token>'

bot = gappy.Bot(TOKEN)
app = Flask(__name__)


@app.route('/', methods=['POST'])
def parse_request():
    msg = request.form
    content_type = msg['type']
    chat_id = msg['chat_id']
    data = msg['data']
    bot.send_text(chat_id, data)
    return 'OK'


if __name__ == '__main__':
    app.run()
```
""",

    url='https://github.com/GapAPy/Gappy/',

    license='GPL',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',

        'License :: OSI Approved :: GNU General Public License (GPL)',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='gap messenger bot api python wrapper',
)
