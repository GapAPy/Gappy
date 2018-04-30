# -*- coding: utf-8 -*-
import time
import json
import threading
import collections
import bisect
import requests
from . import api
from . import exception


__version_info__ = (0, 4, 3)

__version__ = '.'.join(map(str, __version_info__))


class _BotBase(object):
    def __init__(self, token):
        self._token = token
        self._file_chunk_size = 65536


def _strip(params, more=[]):
    return {key: value for key, value in params.items() if key not in ['self'] + more}


def _rectify(params):
    def make_jsonable(value):
        if isinstance(value, list):
            return [make_jsonable(v) for v in value]
        elif isinstance(value, dict):
            return {k: make_jsonable(v) for k, v in value.items() if v is not None}
        elif isinstance(value, tuple) and hasattr(value, '_asdict'):
            return {k: make_jsonable(v) for k, v in value._asdict().items() if v is not None}
        else:
            return value

    def flatten(value):
        v = make_jsonable(value)

        if isinstance(v, (dict, list)):
            return json.dumps(v, separators=(',', ':'))
        else:
            return v

    # remove None, then json-serialize if needed
    return {k: flatten(v) for k, v in params.items() if v is not None}


def t(var_boolean):
    d = {True: 'true',
         False: 'false'}
    return d[var_boolean]


class Bot(_BotBase):
    """
    A class that is sorted by timestamp.

    Use `bisect` module to ensure order in event queue.
    """

    class Scheduler(threading.Thread):
        Event = collections.namedtuple('Event', ['timestamp', 'data'])
        Event.__eq__ = lambda self, other: self.timestamp == other.timestamp
        Event.__ne__ = lambda self, other: self.timestamp != other.timestamp
        Event.__gt__ = lambda self, other: self.timestamp > other.timestamp
        Event.__ge__ = lambda self, other: self.timestamp >= other.timestamp
        Event.__lt__ = lambda self, other: self.timestamp < other.timestamp
        Event.__le__ = lambda self, other: self.timestamp <= other.timestamp

        def __init__(self):
            """Reentrant lock to allow locked method calling locked method."""
            super(Bot.Scheduler, self).__init__()
            self._eventq = []
            self._lock = threading.RLock()
            self._event_handler = None

        def _locked(fn):
            def k(self, *args, **kwargs):
                with self._lock:
                    return fn(self, *args, **kwargs)
            return k

        @_locked
        def _insert_event(self, data, when):
            ev = self.Event(when, data)
            bisect.insort(self._eventq, ev)
            return ev

        @_locked
        def _remove_event(self, event):
            # Find event according to its timestamp.
            # Index returned should be one behind.
            i = bisect.bisect(self._eventq, event)

            """ Having two events with identical timestamp is unlikely but possible.
            I am going to move forward and compare timestamp AND object address
            to make sure the correct object is found."""

            while i > 0:
                i -= 1
                e = self._eventq[i]

                if e.timestamp != event.timestamp:
                    raise exception.EventNotFound(event)
                elif id(e) == id(event):
                    self._eventq.pop(i)
                    return

            raise exception.EventNotFound(event)

        @_locked
        def _pop_expired_event(self):
            if not self._eventq:
                return None

            if self._eventq[0].timestamp <= time.time():
                return self._eventq.pop(0)
            else:
                return None

        def event_at(self, when, data):
            """
            Schedule some data to emit at an absolute timestamp.

            :type when: int or float
            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, when)

        def event_later(self, delay, data):
            """
            Schedule some data to emit after a number of seconds.

            :type delay: int or float
            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, time.time() + delay)

        def event_now(self, data):
            """
            Emit some data as soon as possible.

            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, time.time())

        def cancel(self, event):
            """
            Cancel an event.

            :type event: an internal Event object
            """
            self._remove_event(event)

        def run(self):
            while 1:
                e = self._pop_expired_event()
                while e:
                    if callable(e.data):
                        d = e.data()  # call the data-producing function
                        if d is not None:
                            self._event_handler(d)
                    else:
                        self._event_handler(e.data)

                    e = self._pop_expired_event()
                time.sleep(0.1)

        def run_as_thread(self):
            self.daemon = True
            self.start()

        def on_event(self, fn):
            self._event_handler = fn

    def __init__(self, token):
        """TOKEN."""
        super(Bot, self).__init__(token)
        self._scheduler = self.Scheduler()
        self._last_message = ''

    def _api_request(self, method, params=None, **kwargs):
        if method == 'sendMessage':
            self._last_message = params
        return api.request((self._token, method, params), **kwargs)

    def get_last_message(self):
        return self._last_message

    def send_text(
        self,
        chat_id,
        data,
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send text messages.

        :param chat_id: int
        :param data: str
        :param reply_keyboard: str
        :param inline_keyboard: array
        :param form: json/dict
        :return: array
        """
        type = 'text'
        p = _rectify(_strip(locals()))
        return self._api_request('sendMessage', p)

    def send_image(
        self,
        chat_id,
        image,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Image.

        :param chat_id: int
        :param image: string
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'image'
        try:
            tmp = json.loads(image)
            tmp.update({'desc': desc})
            image = json.dumps(tmp)
            data = image
            del image, desc, tmp
            p = _rectify(_strip(locals()))

        except Exception:
            # if os.path.isfile(image):
                # raise ValueError('Image path is invalid')
            type, data = self.upload_file('image', image, desc)
            del desc
            p = _rectify(_strip(locals()))

        return self._api_request('sendMessage', p)

    def send_audio(
        self,
        chat_id,
        audio,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Audio.

        :param chat_id: int
        :param audio: string
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'audio'
        try:
            tmp = json.loads(audio)
            tmp.update({'desc': desc})
            audio = json.dumps(tmp)
            data = audio
            del audio, desc, tmp
            p = _rectify(_strip(locals()))
        except Exception:
            # if os.path.isfile(audio):
                # raise ValueError('Audio path is invalid')
            type, data = self.upload_file('audio', audio, desc)
            del desc
            p = _rectify(_strip(locals()))

        return self._api_request('sendMessage', p)

    def send_video(
        self,
        chat_id,
        video,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Video.

        :param chat_id: int
        :param video: string
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'video'
        try:
            tmp = json.loads(video)
            tmp.update({'desc': desc})
            video = json.dumps(tmp)
            data = video
            del video, desc, tmp
            p = _rectify(_strip(locals()))
        except Exception:
            # if os.path.isfile(video):
                # raise ValueError('Video path is invalid')
            type, data = self.upload_file('video', video, desc)
            del video, desc
            p = _rectify(_strip(locals()))

        return self._api_request('sendMessage', p)

    def send_file(
        self,
        chat_id,
        file,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send File.

        :param chat_id: int
        :param file: string
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'file'
        try:
            tmp = json.loads(file)
            tmp.update({'desc': desc})
            file = json.dumps(tmp)
            data = file
            del file, desc, tmp
            p = _rectify(_strip(locals()))
        except Exception:
            # if os.path.isfile(file):
                # raise ValueError('File path is invalid')
            type, data = self.upload_file('file', file, desc)
            del desc
            p = _rectify(_strip(locals()))

        return self._api_request('sendMessage', p)

    def send_voice(
        self,
        chat_id,
        voice,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Voice.

        :param chat_id: int
        :param voice: string
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'voice'
        try:
            tmp = json.loads(voice)
            tmp.update({'desc': desc})
            voice = json.dumps(tmp)
            data = voice
            del voice, desc, tmp
            p = _rectify(_strip(locals()))
        except Exception:
            # if os.path.isfile(voice):
                # raise ValueError('Voice path is invalid')
            type, data = self.upload_file('voice', voice, desc)
            del desc
            p = _rectify(_strip(locals()))

        return self._api_request('sendMessage', p)

    def send_action(
        self,
        chat_id,
        action
    ):
        """
        Send Action.

        :param chat_id: int
        :param action: string
        :return: Array
        """
        actions = ['typing']
        if action in actions:
            p = dict(chat_id=chat_id)
            return self._api_request('sendAction', p)

        raise ValueError(
            'Invalid Action! Accepted value: ' + ','.join(actions))

    def send_location(
        self,
        chat_id,
        lat,
        long,
        desc="",
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Location.

        :param chat_id: int
        :param lat: float
        :param long: float
        :param desc: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        data = json.dumps(dict(lat=lat, long=long, desc=desc))
        del lat, long, desc
        type = 'location'
        p = _rectify(_strip(locals()))
        mes = self._api_request('location', p)
        return json.loads(mes)['id'] if mes else False

    def send_contact(
        self,
        chat_id,
        phone,
        name,
        reply_keyboard=None,
        inline_keyboard=None,
        form=None
    ):
        """
        Send Contact.

        :param chat_id: int
        :param phone: string
        :param name: string
        :param reply_keyboard: string
        :param inline_keyboard: array
        :param form: json
        :return: Array
        """
        type = 'contact'
        data = json.dumps(dict(phone=phone, name=name))
        del phone, name
        p = _rectify(_strip(locals()))
        mes = self._api_request('contact', p)
        return json.loads(mes)['id'] if mes else False

    def edit_message(
        self,
        chat_id,
        message_id,
        data=None,
        inline_keyboard=None
    ):
        """
        Edit Message.

        :param chat_id: int
        :param message_id: int
        :param data: string
        :param inline_keyboard: array
        :return: array
        """
        p = _rectify(_strip(locals()))
        return self._api_request('editMessage', p)

    def delete_message(
        self,
        chat_id,
        message_id
    ):
        """
        Delete Message.

        :param chat_id: int
        :param message_id: int
        :return: array
        """
        p = _rectify(_strip(locals()))
        return self._api_request('deleteMessage', p)

    def answer_callback(
        self,
        chat_id,
        callback_id,
        text,
        show_alert=False
    ):
        """
        Answer Callback.

        :param chat_id: int
        :param callback_id: int
        :param text: string
        :param show_alert: boolean
        :return: array
        """
        show_alert = t(show_alert)
        p = _rectify(_strip(locals()))
        return self._api_request('answerCallback', p)

    def send_invoice(
        self,
        chat_id,
        amount,
        description
    ):
        """
        Send Invoice.

        :param chat_id: int
        :param amount: int
        :param description: string
        :return: string
        """
        p = _rectify(_strip(locals()))
        res = self._api_request('invoice', p)
        res = json.loads(res)
        return res['id']

    def pay_verify(
        self,
        chat_id,
        ref_id
    ):
        """
        Pay verify.

        :param chat_id: int
        :param ref_id: int
        :return: boolean
        """
        p = _rectify(_strip(locals()))
        res = self._api_request('payVerify', p)
        res = json.loads(res)
        if isinstance(res, list):
            return res['status'] == 'verified'

    def pay_inquiry(
        self,
        chat_id,
        ref_id
    ):
        """
        Pay inquiry.

        :param chat_id: int
        :param ref_id: int
        :return: boolean
        """
        p = _rectify(_strip(locals()))
        res = self._api_request('payInquiry', p)
        res = json.loads(res)
        if isinstance(res, list):
            return res['status'] == 'verified'

    def request_wallet_charge(
        self,
        chat_id,
        desc=None
    ):
        """
        Request Wallet Charge.

        :param chat_id: int
        :param desc: string
        :return: string
        """
        p = _rectify(_strip(locals()))
        return self._api_request('requestWalletCharge', p)

    def reply_keyboard(
        self,
        keyboard,
        once=True,
        selective=False
    ):
        """
        Reply keyboard.

        :param keyboard: keyboard
        :param once: once
        :param selective: boolean
        :return: boolean
        """
        if isinstance(keyboard, list):
            raise ValueError("Keyboard must be array")
        p = _rectify(_strip(locals()))
        return json.dumps(p)

    def upload_file(
        self,
        content_type,
        file,
        desc=None
    ):

        r = requests.post(
            'https://api.gap.im/upload',
            files={content_type: open(file, 'rb')},
            headers={'token': self._token}
        )
        if r.ok:
            p = json.loads(r.text)
            if desc:
                p.update({'desc': desc})
                return content_type, json.dumps(p)
            else:
                return content_type, json.dumps(p)
        else:
            raise ValueError(r.status_code, r.reason)
