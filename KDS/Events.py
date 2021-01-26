from __future__ import annotations

from typing import Callable, Iterable, Union, overload

new = list()

class Event:
    @overload
    def __init__(self) -> None:
        self.listeners = []
    @overload
    def __init__(self, values: Iterable) -> None:
        self.listeners = [v for v in values]
        
    def __add__(self, value: Event) -> Event:
        if (isinstance(value, Event)):
            if not any(v in value.listeners for v in self.listeners):
                #Creates a new instance
                return Event([*value.listeners, *self.listeners])
            else:
                raise ValueError("Events have overlapping values!")
        else:
            raise TypeError(f"Value of type {type(value)} is not an Event!")
        
    def __iadd__(self, value: Union[Callable[[]], Event]) -> Event:
        if callable(value):
            if value not in self.listeners:
                self.listeners.append(value)
                return self
            else:
                raise ValueError(f"Value {value} already in events!")
        elif isinstance(value, Event):
            if not any(v in value.listeners for v in self.listeners):
                self.listeners.extend(value.listeners)
                return self
            else:
                raise ValueError("Events have overlapping values!")
        else:
            raise TypeError(f"Value of type {type(value)} is not callable and also not an event!")
    
    def __sub__(self, value: Event) -> Event:
        if isinstance(value, Event):
            newVals = []
            for l in self.listeners:
                if l not in value.listeners:
                    newVals.append(l)
            for l in value.listeners:
                if l not in self.listeners and l not in newVals:
                    newVals.append(l)
            return Event(newVals)
        else:
            raise TypeError(f"Value of type {type(value)} is not an Event!")
        
    def __isub__(self, value: Union[Callable[[]], Event]):
        if callable(value):
            while value in self.listeners:
                self.listeners.remove(value)
                return self
        elif isinstance(value, Event):
            for l in self.listeners:
                while l in value.listeners: self.listeners.remove(l)
            return self
        else:
            raise TypeError(f"Value of type {type(value)} is not callable and also not an event!")
        
    def __eq__(self, target: Event) -> bool:
        if isinstance(target, Event):
            return self.listeners == target.listeners
        else:
            raise TypeError(f"Value of type {type(target)} is not an Event!")
    
    def __ne__(self, target: Event) -> bool:
        if isinstance(target, Event):
            return self.listeners != target.listeners
        else:
            raise TypeError(f"Value of type {type(target)} is not an Event!")
    
    def __contains__(self, value: Event) -> bool:
        if isinstance(value, Event):
            return value in self.listeners
        else:
            raise TypeError(f"Value of type {type(value)} is not an Event!")
        
    def __len__(self) -> int:
        return len(self.listeners)
    
    def Invoke(self, *args, **kwargs):
        for listener in self.listeners: listener(*args, **kwargs)
