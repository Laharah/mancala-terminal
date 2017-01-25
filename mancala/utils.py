import functools

def memo(func):
    """
    memoize a function.
    WARNING: no limit on cache, no kwargs, hashable arguments only
    """
    cache = {}
    kwd_mark = object()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args
        if kwargs:
            key +=(kwd_mark,) + tuple(sorted(kwargs.items()))
        try:
            return cache[key]
        except KeyError:
            cache[args] = result = func(*args, **kwargs)
            return result
        except TypeError:
            return func(*args)
    return wrapper
