"""Lazy evaluation for Python.
"""


# From http://stackoverflow.com/questions/9057669/how-can-i-intercept-calls-to-pythons-magic-methods-in-new-style-classes
class Lazy(object):
    """Wrapper class providing __x__ magic methods.

    that provides lazy access to an instance of some
    internal instance.

    self._lazy_func: None or callable
        callable used to create the object.  None otherwise.

    self._lazy_obj: None or object.
        when object is created, it is stored here.  None otherwise.

    self._lazy_make(): method
        method to create the internal object

    self._lazy_clear(): method
        resets self._lazy_obj to None, freeing memory."""

    __wraps__  = None
    __ignore__ = set(("class", "mro", "new", "init",
                      "setattr", "getattr", "getattribute",
                      "dict",
                      "str", "repr", # printing doesn't create object.
                      "reduce_ex", "reduce",  # allow pickle support
                      "getstate", "slots",
                      ))
    #__ignore__ = "class mro new init setattr getattr getattribute dict obj func"
    _lazy_obj      = None
    _lazy_func     = None

    def __init__(self, func):
        """Initialization

        func: callable
            func"""
        if self.__wraps__ is None:
            raise TypeError("base class Wrapper may not be instantiated")
        if not hasattr(func, '__call__'):
            raise TypeError('func %s is not callable'%func)
        self._lazy_func = func
    def _lazy_make(self):
        self._lazy_obj = self._lazy_func()
    def _lazy_clear(self):
        """Clear the saved object"""
        self._lazy_obj = None

    # provide lazy access to regular attributes of wrapped object
    def __getattr__(self, name):
        if self._lazy_func is None:
            # This should only be used during unpickling.  During
            # unpickling, '__func' may not yet be set on the
            # dictionary.
            return
        if self._lazy_obj is None:
            self._lazy_make()
        #print "getattr: %s"%name
        return getattr(self._lazy_obj, name)

    # create proxies for wrapped object's double-underscore
    # attributes, except those in __ignore__
    class __metaclass__(type):
        def __init__(cls, name, bases, dct):
            def make_lazy(name):
                def lazy(self, *args):
                    #print dir(self)
                    #print 'lazy: %s'%name
                    if self._lazy_obj is None:
                        self._lazy_make()
                    return getattr(self._lazy_obj, name)
                return lazy

            type.__init__(cls, name, bases, dct)
            if cls.__wraps__:
                ignore = set("__%s__" % n for n in cls.__ignore__)
                for name in dir(cls.__wraps__):
                    if name.startswith("__"):
                        if name not in ignore and name not in dct:
                            #print name
                            setattr(cls, name, property(make_lazy(name)))

    # Needed for pickle support.  Otherwise tries for __slots__.
    def __getstate__(self):
        """Pickle support, must be defined."""
        return self.__dict__


# These proxies must be explicitly defined in a globally importable
# way.  So any class you might want to proxy, put it here.

import networkx
class NxGraphLazy(Lazy):
    __wraps__ = networkx.Graph



def _test_creator():
    """Helper function for _test.  Must be in globals() for pickling."""
    print "making graph"
    return networkx.complete_graph(10)

def _test():
    from functools import partial
    p = NxGraphLazy(_test_creator)

    assert p._lazy_obj is None
    assert len(p) == 10
    assert p._lazy_obj is not None
    p._lazy_clear()
    assert p._lazy_obj is None

    import cPickle as pickle
    import pickle

    # Test pickling and unpickling.
    print type(p)
    #print p.__dict__
    #from fitz import interactnow
    print "pickling..."
    pkl = pickle.dumps(p)
    print "unpickling..."
    p2 = pickle.loads(pkl)
    print type(p2)
    #print len(p2)
    assert p2._lazy_obj is None
    print [x for x in p2]
    assert p2._lazy_obj is not None

    p2._lazy_clear()
    assert p2._lazy_obj is None

if __name__ == '__main__':
    _test()
