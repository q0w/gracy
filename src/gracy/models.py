import copy
import logging
import typing
from dataclasses import dataclass
from enum import Enum, IntEnum
from http import HTTPStatus
from typing import Final, Iterable


class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


@dataclass
class LogEvent:
    level: LogLevel


class Unset:
    """
    The default "unset" state indicates that whatever default is set on the
    client should be used. This is different to setting `None`, which
    explicitly disables the parameter, possibly overriding a client default.
    """


UNSET_VALUE: Final = Unset()

LOG_EVENT_TYPE = None | Unset | LogEvent


# TODO: Allowed status code / strict status code / retry / throttle / parser
@dataclass
class GracyConfig:
    log_request: LOG_EVENT_TYPE
    log_response: LOG_EVENT_TYPE
    log_errors: LOG_EVENT_TYPE

    strict_status_code: Iterable[HTTPStatus] | HTTPStatus | Unset
    """Stricitly enforces only one or many HTTP Status code to be considered as successful.

    e.g. Setting it to 201 would raise exceptions for both 204 or 200"""

    allowed_status_code: Iterable[HTTPStatus] | HTTPStatus | Unset
    """Adds one or many HTTP Status code that would normally be considered an error

    e.g. 404 would consider any 200-299 and 404 as successful."""


DEFAULT_CONFIG: Final = GracyConfig(
    log_request=None,
    log_response=None,
    log_errors=LogEvent(LogLevel.ERROR),
    strict_status_code=UNSET_VALUE,
    allowed_status_code=UNSET_VALUE,
)


def customize_config(base: GracyConfig, modifier: GracyConfig):
    new_obj = copy.copy(base)
    for key, value in vars(modifier).items():
        if getattr(new_obj, key) is None:
            setattr(new_obj, key, value)

    return new_obj


class BaseEndpoint(str, Enum):
    pass


@dataclass
class GracefulMethod:
    config: GracyConfig
    function: typing.Callable[..., typing.Any]

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        return self.function(*args, **kwargs)
