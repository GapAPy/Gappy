Gappy
==========

Python framework for Gap Service API

#[![Build Status](https://travis-ci.org/itmard/Persian.png?branch=master)](https://travis-ci.org/itmard/Persian)

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
from import Flask, request

TOKEN = '<your token>'

bot = gappy.Bot(TOKEN)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def parse_request():
    msg =request.form
    content_type = msg['type']    
    chat_id = msg['chat_id']      
    data = msg['data']
    bot.send_text(chat_id, data)
    return 'OK'
```


### Contributors

- [Sadegh Yazdani](http://pypro.blog.ir/)
- [HsiN75](https://Hsin75.ir)
- [Mostafa Asadi](https://ma73.ir)

### Contributing

This is a open-source project. Fork the project, complete the code and send pull request.

 
