"""Utilities for static type checking"""

from typing import ParamSpec, TypeVar, Any, cast, final, Self
from collections.abc import Callable

P = ParamSpec("P")
T = TypeVar("T")



# https://stackoverflow.com/questions/71968447/python-typing-copy-kwargs-from-one-function-to-another
def copy_method_params(
    _source_function: Callable[P, Any]
) -> Callable[[Callable[..., T]], Callable[P, T]]:
    """Decorator does nothing but returning the casted original function"""

    def return_func(destination_function: Callable[..., T]) -> Callable[P, T]:
        return cast(Callable[P, T], destination_function)

    return return_func

class Abstract:
    def __new__(cls, *args:Any, **kwargs:Any) -> Self:
        print(cls)
        if getattr(cls,"__abstract__",False):
            raise TypeError("Initializing abstract base class")
        return super().__new__(cls,*args,**kwargs)
