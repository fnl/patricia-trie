"""
.. py:module:: patricia
   :synopsis: A PATRICIA trie implementation.

A PATRICIA trie implementation for efficient matching of string collections on
text.

This class has an (Py2.7+) API nearly equal to dictionaries.

*Deleting* entries is a "half-supported" operation only. The key appears
"removed", but the trie is not actually changed, only the node state is
changed from terminal to non-terminal. I.e., if you frequently delete keys,
the compaction will become fragmented and less efficient. To mitigate this
effect, make a copy of the trie (using a copy constructor idiom)::

    T = trie(**T)

If you are only interested in scanning for the *presence* of keys, but do not
care about mapping a value to each key, using ``None`` as the value of your
keys and scanning with ``key(S, None, start=i)`` at every offset ``i`` in the
string ``S`` is perfectly fine (because the return value will be the key
string iff a full match was made and ``None`` otherwise)::

>>> T = trie(present=None)
>>> T.key('is absent here', None, start=3) # start scanning at offset 3
>>> T.key('is present here', None, start=3) # start scanning at offset 3
'present'

.. moduleauthor:: Florian Leitner <florian.leitner@gmail.com>
.. License: Apache License v2 (http://www.apache.org/licenses/LICENSE-2.0.html)
"""

__author__ = 'Florian Leitner'
__version__ = '5'

class _NonTerminal(): pass
__NON_TERMINAL__ = _NonTerminal()

# recursive functions

def _count(node):
    "Count the number of terminal nodes in this branch."
    count = 0 if (node._value is __NON_TERMINAL__) else 1
    for _, child in node._edges:
        count += _count(child)
    return count

def _keys(node, accu):
    "Yield keys of terminal nodes in this branch."
    for key, value in _items(node, accu):
        yield key

def _items(node, accu):
    "Yield key, value pairs of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield ''.join(accu), node._value
    for edge, child in node._edges:
        accu.append(edge)
        for key, value in _items(child, accu):
            yield key, value
        accu.pop()

def _values(node):
    "Yield values of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield node._value
    for edge, child in node._edges:
        for value in _values(child):
            yield value

# main class

class trie():
    """
    **Usage Example**::

    >>> T = trie(None, key='value', king='kong') # a root value and two pairs
    >>> '' in T # check if the value exits (note: the [empty] root is '')
    True
    >>> 'kong' in T
    False
    >>> T['king'] # get the value for an exact key
    'kong'
    >>> T['kong'] # error from non-existing keys
    Traceback (most recent call last):
        ...
    KeyError: 'kong'
    >>> len(T) # count keys ("terminals") in the tree
    3
    >>> sorted(T.keys()) # "traditional stuff": keys(), values(), and items()
    ['', 'key', 'king']
    >>> # scanning a text S with key(S), value(S), and item(S):
    >>> S = 'keys and kewl stuff'
    >>> T.key(S) # report the (longest) key that is a prefix of S
    'key'
    >>> T.value(S, start=9) # using offsets; NB: empty root always matches!
    >>> del T[''] # interlude: deleting keys and root is the empty key
    >>> T.item(S, start=9) # raise error if no key is a prefix of S
    Traceback (most recent call last):
        ...
    KeyError: 'k'
    >>> # info: the error string above contains the matched path so far
    >>> T.item(S, None, 9) # avoid the error by specifying a default
    (None, None)
    >>> # iterate all matching content with keys(S), values(S), and items(S):
    >>> list(T.items(S))
    [('key', 'value')]
    >>> T.isPrefix('k') # reverse lookup: check if S is a prefix of any key
    True
    >>> T.isPrefix('kong')
    False
    >>> sorted(T.iter('k')) # and get all keys that have S as prefix
    ['key', 'king']
    """

    def __init__(self, *value, **keys):
        """
        Create a new node.
        Any arguments will be used as the ``value`` of this node.
        If keyword arguments are given, they initialize a whole branch.
        Note that ``None`` is a valid value for a node.
        """
        self._edges = []
        self._value = __NON_TERMINAL__
        if len(value):
            if len(value) == 1:
                self._value = value[0]
            else:
                self._value = value
        for key, val in keys.items():
            self[key] = val

    def _find(self, path, offset):
        for edge, child in self._edges:
            if path.startswith(edge, offset):
                return child, offset + len(edge)
        else:
            return None, offset # return None

    def _next(self, path, offset):
        for edge, child in self._edges:
            if path.startswith(edge, offset):
                return child, offset + len(edge)
        else:
            raise KeyError(path) # raise error

    def _scan(self, string, rval_fun, idx):
        node = self
        while node is not None:
            if node._value is not __NON_TERMINAL__:
                yield rval_fun(string, idx, node._value)
            node, idx = node._find(string, idx)

    def __setitem__(self, key, value):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            for edge, child in node._edges:
                # if the whole prefix matches, advance:
                if key.startswith(edge, idx):
                    node = child
                    idx += len(edge)
                    break
                # split edge if prefix matches (part of) the key:
                elif edge[0] == key[idx]:
                    # and split on the longest common prefix
                    pos = 1
                    last = min(len(edge), keylen - idx)
                    while pos < last and edge[pos] == key[idx + pos]:
                        pos += 1
                    split = trie()
                    split._edges.append((edge[pos:], child))
                    node._edges.remove((edge, child))
                    node._edges.append((edge[:pos], split))
                    node = split
                    idx += pos
                    break
            # no common prefix, create a completely new node
            else:
                node._edges.append((key[idx:], trie(value)))
                break
        else:
            node._value = value

    def __getitem__(self, key):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            node, idx = node._next(key, idx)
        if node._value is __NON_TERMINAL__:
            raise KeyError(key)
        else:
            return node._value

    def __delitem__(self, key):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            node, idx = node._next(key, idx)
        if node._value is __NON_TERMINAL__:
            raise KeyError(key)
        node._value = __NON_TERMINAL__

    def __contains__(self, key):
        node = self
        keylen = len(key)
        idx = 0
        while idx != keylen and node is not None:
            node, idx = node._find(key, idx)
        return False if node is None else (node._value is not __NON_TERMINAL__)

    def __iter__(self):
        return _keys(self, [])

    def __len__(self):
        return _count(self)

    def __repr__(self):
        string = ['trie({']
        first = True
        for key, value in _items(self, []):
            if first: first = False
            else: string.append(', ')
            string.append(repr(key))
            string.append(': ')
            string.append(repr(value))
        string.append('})')
        return ''.join(string)

    def key(self, string, default=__NON_TERMINAL__, start=0):
        """
        Return the longest key that is a prefix of ``string`` (beginning at
        ``start``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, default, start)[0]

    def keys(self, string=None, start=0):
        """
        Return all keys (that are a prefix of ``string`` (beginning at
        ``start``)).
        """
        if string is None:
            return _keys(self, [])
        else:
            return self._scan(
                string, (lambda string, idx, value: string[start:idx]), start
            )

    def value(self, string, default=__NON_TERMINAL__, start=0):
        """
        Return the value of the longest key that is a prefix of ``string``
        (beginning at ``start``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, default, start)[1]

    def values(self, string=None, start=0):
        """
        Return all values (for keys that are a prefix of ``string`` (starting
        at ``start``)).
        """
        if string is None:
            return _values(self)
        else:
            return self._scan(string, (lambda string, i, value: value), start)

    def item(self, string, default=__NON_TERMINAL__, start=0):
        """
        Return the key, value pair of the longest key that is a prefix of
        ``string`` (beginning at ``start``).
        If no key matches, raise a `KeyError` or return the ``None``,
        ``default`` pair if any ``default`` value was set.
        """
        node = self
        strlen = len(string)
        idx = start
        last = self._value
        while idx < strlen:
            node, idx = node._find(string, idx)
            if node is None:
                break
            elif node._value is not __NON_TERMINAL__:
                last = node._value
        if last is not __NON_TERMINAL__:
            return string[start:idx], last
        elif default is not __NON_TERMINAL__:
            return None, default
        else:
            raise KeyError(string[start:idx])

    def items(self, string=None, start=0):
        """
        Return all key, value pairs (for keys that are a prefix of ``string``
        (beginning at ``start``)).
        """
        if string is None:
            return _items(self, [])
        else:
            return self._scan(
                string,
                (lambda string, idx, value: (string[start:idx], value)),
                start
            )

    def isPrefix(self, string):
        "Return True if any key starts with ``string``."
        node = self
        strlen = len(string)
        idx = 0
        while idx < strlen:
            len_left = strlen - idx
            for edge, child in node._edges:
                prefix = edge[:len_left] if (len_left < len(edge)) else edge
                if string.startswith(prefix, idx):
                    node = child
                    idx += len(edge)
                    break
            else:
                return False
        return True

    def iter(self, prefix):
        "Return an iterator over all keys that start with ``prefix``."
        node = self
        plen = len(prefix)
        idx = 0
        while idx < plen:
            try:
                node, idx = node._next(prefix, idx)
            except KeyError:
                break
        accu = [prefix]
        if idx != plen:
            remainder = prefix[idx:]
            for edge, child in node._edges:
                if edge.startswith(remainder):
                    node = child
                    accu.append(edge[len(remainder):])
                    break
            else:
                return iter([])
        return _keys(node, accu)
