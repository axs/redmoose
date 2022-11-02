import logging
import typing

log = logging.getLogger(__name__)


class ServiceRegistry:
    def __init__(self):
        self._lookup = {}

    def add(self, service_id: typing.Tuple, service):
        registered_service = self._lookup.get(service_id)
        if not registered_service:
            log.info(f"registering {service_id}")
            self._lookup[service_id] = service

    def get_service(self, service_id: typing.Tuple):
        return self._lookup.get(service_id)

    def create_service(self, service_id: typing.Tuple, **kwargs):
        c = self._lookup.get(service_id)
        try:
            return c(**kwargs)
        except TypeError as t:
            log.exception(t)

    def register(self, service_id: typing.Tuple) -> typing.Callable:
        """
        In [42]: s=ServiceRegistry()

        In [43]: @s.register((2,3,5))
            ...: class Ex:
            ...:     def __init__(self, **kwargs):
            ...:         self.t=54
            ...:     def execute(self,r):
            ...:         return self.t + r
            ...:
        Args:
            service_id:
        Returns: class decorator
        """

        def inner_wrapper(wrapped_class) -> typing.Callable:
            if service_id in self._lookup:
                log.warning('Executor %s already exists. Will replace it', service_id)
            self._lookup[service_id] = wrapped_class
            return wrapped_class

        return inner_wrapper
