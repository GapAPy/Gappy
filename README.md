# Gappy
## Python framework for [Gap Service API](https://developer.gap.im/)
[![Travis](https://img.shields.io/travis/GapAPy/Gappy.svg?style=for-the-badge)](https://travis-ci.org/GapAPy/Gappy)
[![GitHub last commit](https://img.shields.io/github/last-commit/GapAPy/Gappy.svg?style=for-the-badge)](https://github.com/GapAPy/Gappy/commits/master)
[![GitHub contributors](https://img.shields.io/github/contributors/GapAPy/Gappy.svg?style=for-the-badge)](https://github.com/GapAPy/Gappy/graphs/contributors)
[![PyPI](https://img.shields.io/pypi/v/gappy.svg?style=for-the-badge)](https://pypi.org/project/gappy/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gappy.svg?style=for-the-badge)](https://pypi.org/project/gappy/)
[![license](https://img.shields.io/github/license/GapAPy/Gappy.svg?style=for-the-badge)](https://github.com/GapAPy/Gappy/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/GapAPy/Gappy.svg?style=for-the-badge&label=Stars)](https://github.com/GapAPy/Gappy)


## Install
### PyPI
```
pip3 install gappy
```
### Git
```
git clone https://github.com/GapAPy/Gappy/
cd Gappy
python3 setup.py install
```

## Usage

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
- [more information](https://developer.gap.im/documents/fa/)


## [Authors](https://github.com/GapAPy/Gappy/graphs/contributors)

- [**Sadegh Yazdani**](http://pypro.blog.ir/) [Github](https://github.com/aerosadegh) [*Silverstar10@gmail.com*](Silverstar10@gmail.com)
- [**HsiN75**](https://Hsin75.ir) [Github](https://github.com/hsin75) [*hsin0475@gmail.com*](hsin0475@gmail.com)
- [**Mostafa Asadi**](https://ma73.ir) [Github](https://github.com/mostafaasadi) [*mostafaasadi73@gmail.com*](mostafaasadi73@gmail.com)

#### See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Contributing

#### This is a open-source project. Fork the project, complete the code and send pull request.

## License

#### This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details
