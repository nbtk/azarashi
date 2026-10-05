"""Keyword arguments of earlier versions, taken under their earlier names."""
import functools
import inspect
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, cast

from ..exceptions import AzarashiArgumentTypeError

P = ParamSpec('P')
R = TypeVar('R')


def takes_msg_type(function: Callable[P, R]) -> Callable[P, R]:
    """Let the function take msg_format under its earlier name, msg_type."""
    signature = inspect.signature(function)

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        given = cast(dict[str, Any], kwargs)
        if 'msg_type' in given:
            msg_type = given.pop('msg_type')
            if 'msg_format' in signature.bind_partial(*args, **given).arguments:
                raise AzarashiArgumentTypeError(
                    f'{function.__name__}() takes msg_format or its earlier name msg_type, not both')
            given['msg_format'] = msg_type
        return function(*args, **kwargs)

    return wrapper
