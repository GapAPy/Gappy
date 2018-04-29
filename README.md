# Gappy
## Python framework for Gap Service API
[![Build Status](https://travis-ci.org/GapAPy/Gappy.svg?branch=master)](https://travis-ci.org/GapAPy/Gappy) 
### Install Package
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


### Contributors

- [Sadegh Yazdani](http://pypro.blog.ir/)
- [HsiN75](https://Hsin75.ir)
- [Mostafa Asadi](https://ma73.ir)

### Contributing

This is a open-source project. Fork the project, complete the code and send pull request.
