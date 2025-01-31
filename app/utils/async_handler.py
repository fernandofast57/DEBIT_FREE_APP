
import asyncio
from typing import Callable, Dict, List, Any
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AsyncEventHandler:
    def __init__(self):
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._loop = None

    def get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    async def emit(self, event_name: str, *args, **kwargs):
        if event_name in self._event_handlers:
            results = []
            for handler in self._event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await asyncio.wait_for(handler(*args, **kwargs), timeout=10.0)
                    else:
                        result = await self.get_loop().run_in_executor(None, handler, *args, **kwargs)
                    results.append(result)
                except asyncio.TimeoutError:
                    logger.error(f"Handler timeout for event {event_name}")
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")
                    continue
            return results

    def register_event_handler(self, event_name: str):
        def decorator(f):
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append(f)
            return f
        return decorator

event_handler = AsyncEventHandler()

def async_handler(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in async handler: {str(e)}")
            raise
    return wrapper
