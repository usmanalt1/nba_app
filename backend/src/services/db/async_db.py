import asyncio
from typing import Callable, TypeVar

from django.db import close_old_connections

T = TypeVar("T")


async def db_thread(fn: Callable[..., T], *args, **kwargs) -> T:
    """Run ORM work off the event loop, then release the worker thread's connection.

    Django recycles connections only on the request thread, so one opened inside a
    bare asyncio.to_thread is never checked again and fails once Neon drops it.
    """
    def call() -> T:
        try:
            return fn(*args, **kwargs)
        finally:
            close_old_connections()

    return await asyncio.to_thread(call)
