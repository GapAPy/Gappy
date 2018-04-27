# -*- coding: utf-8 -*-


class GappyException(Exception):
    """Base class of following exceptions."""

    pass


class BadFlavor(GappyException):
    def __init__(self, offender):
        super(BadFlavor, self).__init__(offender)

    @property
    def offender(self):
        return self.args[0]


class BadHTTPResponse(GappyException):
    """
    All requests to Bot API should result in a JSON response.

    If non-JSON, this exception is raised. While it is hard to pinpoint exactly
    when this might happen,
    the following situations have been observed to give rise to it:

    - an unreasonable token, e.g. ``abc``, ``123``, anything that does not even
      remotely resemble a correct token.
    - a bad gateway, e.g. when Gap servers are down.
    """

    def __init__(self, status, text, response):
        super(BadHTTPResponse, self).__init__(status, text, response)

    @property
    def status(self):
        return self.args[0]

    @property
    def text(self):
        return self.args[1]

    @property
    def response(self):
        return self.args[2]


class EventNotFound(GappyException):
    def __init__(self, event):
        super(EventNotFound, self).__init__(event)

    @property
    def event(self):
        return self.args[0]


class WaitTooLong(GappyException):
    def __init__(self, seconds):
        super(WaitTooLong, self).__init__(seconds)

    @property
    def seconds(self):
        return self.args[0]


class IdleTerminate(WaitTooLong):
    pass


class StopListening(GappyException):
    pass


class GapError(GappyException):
    """
    Gap Error.

    To indicate erroneous situations, Gap returns a JSON object containing
    an *error code* and a *description*.
    This will cause a ``GapError`` to
    be raised. Before raising a generic ``GapError``, telepot looks for
    a more specific subclass that "matches" the error. If such a class exists,
    an exception of that specific subclass is raised. This allows you to either
    catch specific errors or to cast a wide net (by a catch-all ``GapError``).
    This also allows you to incorporate custom ``GapError`` easily.
    """

    def __init__(self, description, json):
        super(GapError, self).__init__(description, json)

    @property
    def description(self):
        return self.args[0]

    @property
    def json(self):
        return self.args[1]
