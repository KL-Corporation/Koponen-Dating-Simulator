from __future__ import annotations

from typing import Any, Callable, Iterable, Union

import KDS.Linq

new = list()

# Currently no useful type hints, because I suck at Python
class Event:
    def __init__(self, values: Iterable[Callable] = []) -> None:
        self.listeners = [v for v in values]

    def __add__(self, value: Event) -> Event:
        if (isinstance(value, Event)):
            toAdd = KDS.Linq.Where(value.listeners, lambda v: v not in self.listeners)
            return Event([*self.listeners, *toAdd]) # Makes a new instance by unpacking two lists to a new list.
            # else:
            #     raise ValueError("Events have overlapping values!")
        else:
            raise TypeError(f"Value of type {type(value)} is not an Event!")

    def __iadd__(self, value: Union[Callable, Event]) -> Event:
        if callable(value):
            if value not in self.listeners:
                self.listeners.append(value)
            return self
            # else: Maybe throwing an error is a bit too much
            #     raise ValueError(f"Value {value} already in events!")
        elif isinstance(value, Event):
            toAdd = KDS.Linq.Where(value.listeners, lambda v: v not in self.listeners)
            self.listeners.extend(toAdd)
            return self
            # else:
            #     raise ValueError("Events have overlapping values!")
        else:
            raise TypeError(f"Value of type {type(value)} is not callable and also not an event!")

    def __sub__(self, value: Event) -> Event:
        if isinstance(value, Event):
            newValues = KDS.Linq.Where(value.listeners, lambda v: v not in self.listeners)
            return Event(newValues)
        else:
            raise TypeError(f"Value of type {type(value)} is not an Event!")

    def __isub__(self, value: Union[Callable, Event]):
        if callable(value):
            while value in self.listeners:
                self.listeners.remove(value)
        elif isinstance(value, Event):
            toRemove = KDS.Linq.Where(value.listeners, lambda v: v in self.listeners)
            for rem in toRemove:
                self.listeners.remove(rem) # No need to check for duplicates, there should not be any.
        else:
            raise TypeError(f"Value of type {type(value)} is not callable and also not an event!")
        return self

    def __eq__(self, target: Event) -> bool:
        if isinstance(target, Event):
            return self.listeners == target.listeners
        else:
            return False

    def __ne__(self, target: Event) -> bool:
        return not self.__eq__(target)

    def __contains__(self, value: Callable) -> bool:
        return value in self.listeners # Will return False if wrong type.

    def __len__(self) -> int:
        return len(self.listeners)

    def Invoke(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)
