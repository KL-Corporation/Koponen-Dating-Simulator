from typing import Callable, Iterable, TypeVar, Union, cast

TSource = TypeVar("TSource", bound=object)
TSelector = TypeVar("TSelector", int, float)

def Any(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> bool:
    """Determines whether any element of an iterable satisfies a condition.

    Args:
        source (Iterable[TSource]): An Iterable whose elements to apply the predicate to.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        bool: True if the source iterable is not empty and at least one of its elements passes the test in the specified predicate; otherwise, False.
    """
    for v in source:
        if predicate(v) == True:
            return True
    return False

def All(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> bool:
    """Determines whether all elements of an iterable satisfy a condition.

    Args:
        source (Iterable[TSource]): An Iterable that contains the elements to apply the predicate to.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        bool: True if every element of the source iterable passes the test in the specified predicate, or if the iterable is empty; otherwise, False.
    """
    for v in source:
        if predicate(v) == False:
            return False
    return True

def Average(source: Iterable[TSource], predicate: Callable[[TSource], Union[int, float]]) -> float:
    r = 0
    i = 0
    for v in source:
        r += predicate(v)
        i += 1
    return (r / i if i > 0 else -1)

def Contains(source: Iterable[TSource], value: TSource, comparer: Callable[[TSource, TSource], bool]) -> bool:
    """Determines whether an iterable contains a specified element by using a specified comparer.

    Args:
        source (Iterable[TSource]): an iterable in which to locate a value.
        value (TSource): The value to locate in the iterable.
        comparer (Callable[[TSource, TSource], bool]): An equality comparer to compare values.

    Returns:
        bool: True if the source iterable contains an element that has the specified value; otherwise, False.
    """
    for v in source:
        if comparer(v, value) == True:
            return True
    return False

def Count(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> int:
    """Returns a number that represents how many elements in the specified iterable satisfy a condition.

    Args:
        source (Iterable[TSource]): an iterable that contains elements to be tested and counted.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        int: A number that represents how many elements in the iterable satisfy the condition in the predicate function.
    """
    c = 0
    for v in source:
        if predicate(v):
            c += 1
    return c

def Sum(source: Iterable[TSource], selector: Callable[[TSource], TSelector]) -> TSelector:
    """Computes the sum of the iterable of values that are obtained by invoking a transform function on each element of the input iterable.

    Args:
        source (Iterable[TValue]): an iterable of values that are used to calculate a sum.
        selector (Callable[[TValue], TValue]): A transform function to apply to each element.

    Returns:
        TValue: The sum of the projected values.
    """
    r = cast(TSelector, 0)
    for v in source:
        r += selector(v)
    return r

def Where(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Iterable[TSource]: # User can convert this to tuple by using "tuple()"
    """Filters an iterable of values based on a predicate.

    Args:
        source (Iterable[TSource]): An Iterable to filter.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        Iterable[TSource]: An Iterable that contains elements from the input iterable that satisfy the condition.
    """
    return filter(predicate, source)

def First(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> TSource:
    """Returns the first element of a sequence that satisfies a specified condition.

    Args:
        source (Iterable[TSource]): The Iterable to return the first element of.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Raises:
        LookupError: No element satisfies the condition in predicate.

    Returns:
        TSource: The first element in the iterable that passes the test in the specified predicate function.
    """
    for v in source:
        if predicate(v) == True:
            return v
    raise LookupError("No element satisfies the condition in predicate.")

def FirstOrNone(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Union[TSource, None]:
    """Returns the first element of the iterable that satisfies a condition or None if no such element is found.

    Args:
        source (Iterable[TSource]): The Iterable to return the first element of.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        Union[TSource, None]: None if source is empty or if no element passes the test specified by predicate; otherwise, the first element in source that passes the test specified by predicate.
    """
    # Not calling First and catching an exception because catching exceptions is slow as hell
    for v in source:
        if predicate(v) == True:
            return v
    return None

def Last(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> TSource:
    """Returns the last element of a sequence that satisfies a specified condition.

    Args:
        source (Iterable[TSource]): The Iterable to return the first element of.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Raises:
        LookupError: No element satisfies the condition in predicate.

    Returns:
        TSource: The first element in the iterable that passes the test in the specified predicate function.
    """
    for v in reversed(tuple(source)): # This will be fucking slow, but Iterables cannot be reversed.
        if predicate(v) == True:
            return v
    raise LookupError("No element satisfies the condition in predicate.")

def LastOrNone(source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Union[TSource, None]:
    """Returns the last element of the iterable that satisfies a condition or None if no such element is found.

    Args:
        source (Iterable[TSource]): The Iterable to return the first element of.
        predicate (Callable[[TSource], bool]): A function to test each element for a condition.

    Returns:
        Union[TSource, None]: None if source is empty or if no element passes the test specified by predicate; otherwise, the first element in source that passes the test specified by predicate.
    """
    # Not calling Last and catching an exception because catching exceptions is slow as hell

    for v in reversed(tuple(source)): # This will be fucking slow, but Iterables cannot be reversed.
        if predicate(v) == True:
            return v
    return None