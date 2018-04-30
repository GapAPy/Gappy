# -*- coding: utf-8 -*-
import json
import requests
from . import exception


def _methodurl(req, **user_kw):
    token, method, params = req
    return 'https://api.gap.im/%s' % (method)


def _fix_type(v):
    return str(v) if isinstance(v, float) else v


def _compose_fields(req, **user_kw):
    token, method, params = req
    fields = {k: _fix_type(v) for k, v in params.items()} if params is not None else {}
    return fields


def _transform(req, **user_kw):
    token, method, params = req
    fields = _compose_fields(req, **user_kw)
    url = _methodurl(req, **user_kw)
    headers = {'token': token}
    if method == 'upload':
        return requests.post, {'url': url, 'files': fields, 'headers': headers}        
    else:
        return requests.post, {'url': url, 'data': fields, 'headers': headers}


def _parse(response):
    try:
        text = response.text
        data = json.loads(text)
    except ValueError:  # No JSON object could be decoded
        raise exception.BadHTTPResponse(
            response.status_code,
            text,
            response.reason)

    if response.ok:
        return data
    else:
        description = data['error']
        # raise generic error
        raise exception.GapError(description, data)


def request(req, **user_kw):
    fn, kwargs = _transform(req, **user_kw)
    r = fn(**kwargs)  # `fn` must be thread-safe
    return _parse(r)
