# coding: utf-8


class FactoryNotRegisteredExeption(Exception):
    pass


class Registered(dict):

    def __getitem__(self, key):
        value = self.get(key, key)
        if isinstance(value, str):
            raise FactoryNotRegisteredExeption("{} factory is not registered".format(key))
        return value


registered_factories = Registered()
