"""
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
care about mapping a value to each key, using `None` as the value of your
keys and scanning with ``key(S, i, j, None)`` at every offset ``i:j`` in the
string ``S`` is perfectly fine (because the return value will be the key
string iff a full match was made and `None` otherwise). In other words, it
is not necessary to create slices of strings to scan in a window only::

    >>> T = trie(present=None)
    >>> T.key('is absent here', 3, 9, None) # scan in second word [3:9]
    >>> T.key('is present here', 3, 10, None) # scan in second word [3:10]
    'present'

License: Apache License v2 (http://www.apache.org/licenses/LICENSE-2.0.html)
"""

__author__ = 'Florian Leitner <florian.leitner@gmail.com>'
__version__ = '8'


class _NonTerminal(): pass


__NON_TERMINAL__ = _NonTerminal()

# recursive functions

def _count(node):
    "Count the number of terminal nodes in this branch."
    count = 0 if (node._value is __NON_TERMINAL__) else 1
    for _, child in node._edges.values():
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
    for edge, child in node._edges.values():
        accu.append(edge)
        for key, value in _items(child, accu):
            yield key, value
        accu.pop()


def _values(node):
    "Yield values of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield node._value
    for edge, child in node._edges.values():
        for value in _values(child):
            yield value

# main class

class trie():
    """
    Usage Example::

      >>> T = trie('root', key='value', king='kong') # a root and two nodes
      >>> T['four'] = None # setting new values as in a dict
      >>> '' in T # check if the value exits (note: the [empty] root is '')
      True
      >>> 'kong' in T # existence checks as in a dict
      False
      >>> T['king'] # get the value for an exact key ... as in a dict!
      'kong'
      >>> T['kong'] # error from non-existing keys (as in a dict...)
      Traceback (most recent call last):
          ...
      KeyError: 'kong'
      >>> len(T) # count keys ("terminals") in the tree
      4
      >>> sorted(T) # plus "traditional stuff": keys(), values(), and items()
      ['', 'four', 'key', 'king']
      >>> # scanning a text S with key(S), value(S), and item(S):
      >>> S = 'keys and kewl stuff'
      >>> T.key(S) # report the (longest) key that is a prefix of S
      'key'
      >>> T.value(S, 9) # using offsets; NB: empty root always matches!
      'root'
      >>> del T[''] # interlude: deleting keys and root is the empty key
      >>> T.item(S, 9) # raise error if no key is a prefix of S
      Traceback (most recent call last):
          ...
      KeyError: 'k'
      >>> # info: the error string above contains the matched path so far
      >>> T.item(S, 9, default=None) # avoid the error by specifying a default
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

    def __init__(self, *value, **branch):
        """
        Create a new tree node.
        Any arguments will be used as the ``value`` of this node.
        If keyword arguments are given, they initialize a whole ``branch``.
        Note that `None` is a valid value for a node.
        """
        self._edges = {}
        self._value = __NON_TERMINAL__
        if len(value):
            if len(value) == 1:
                self._value = value[0]
            else:
                self._value = value
        for key, val in branch.items():
            self[key] = val

    def _find(self, path, start, *end):
        if path[start] in self._edges:
            edge, child = self._edges[path[start]]
            if path.startswith(edge, start, *end):
                return child, start + len(edge)
        return None, start # return None

    def _next(self, path, start, *end):
        try:
            edge, child = self._edges[path[start]]
            if path.startswith(edge, start, *end):
                return child, start + len(edge)
        except KeyError:
            pass
        raise KeyError(path) # raise error

    def _scan(self, rvalFun, string, start=0, *end):
        node = self
        if start < 0:
            start = max(0, len(string) + start)
        while node is not None:
            if node._value is not __NON_TERMINAL__:
                yield rvalFun(string, start, node._value)
            node, start = node._find(string, start, *end)

    def __setitem__(self, key, value):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            if key[idx] in node._edges:
                edge, child = node._edges[key[idx]]
                if key.startswith(edge, idx):
                    # the whole prefix matches; advance
                    node = child
                    idx += len(edge)
                else:
                    # split edge after the matching part of the key
                    pos = 1
                    last = min(len(edge), keylen - idx)
                    while pos < last and edge[pos] == key[idx + pos]:
                        pos += 1
                    split = trie()
                    split._edges[edge[pos]] = (edge[pos:], child)
                    node._edges[key[idx]] = (edge[:pos], split)
                    node = split
                    idx += pos
            else:
                # no common prefix, create a new edge and (leaf) node
                node._edges[key[idx]] = (key[idx:], trie(value))
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
            if first:
                first = False
            else:
                string.append(', ')
            string.append(repr(key))
            string.append(': ')
            string.append(repr(value))
        string.append('})')
        return ''.join(string)

    def key(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the longest key that is a prefix of ``string`` (beginning at
        ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, start, end, default)[0]

    def keys(self, *scan):
        """
        Return all keys (that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _keys(self, [])
        else:
            if l == 1: scan = (scan[0], 0)
            getKey = lambda string, idx, value: string[scan[1]:idx]
            return self._scan(getKey, *scan)

    def value(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the value of the longest key that is a prefix of ``string``
        (beginning at ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, start, end, default)[1]

    def values(self, *scan):
        """
        Return all values (for keys that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _values(self)
        else:
            if l == 1: scan = (scan[0], 0)
            getValue = lambda string, idx, value: value
            return self._scan(getValue, *scan)

    def item(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the key, value pair of the longest key that is a prefix of
        ``string`` (beginning at ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the `None`,
        ``default`` pair if any ``default`` value was set.
        """
        node = self
        strlen = len(string)
        if start < 0:
            start = max(0, strlen + start)
        end = strlen if end is None else end
        idx = start
        last = self._value
        while idx < strlen:
            node, idx = node._find(string, idx, end)
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

    def items(self, *scan):
        """
        Return all key, value pairs (for keys that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _items(self, [])
        else:
            if l == 1: scan = (scan[0], 0)
            getItem = lambda string, idx, value: (string[scan[1]:idx], value)
            return self._scan(getItem, *scan)

    def isPrefix(self, prefix):
        "Return True if any key starts with ``prefix``."
        node = self
        plen = len(prefix)
        idx = 0
        while idx < plen:
            len_left = plen - idx
            for edge, child in node._edges.values():
                e = edge[:len_left] if (len_left < len(edge)) else edge
                if prefix.startswith(e, idx):
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
            for edge, child in node._edges.values():
                if edge.startswith(remainder):
                    node = child
                    accu.append(edge[len(remainder):])
                    break
            else:
                return iter([])
        return _keys(node, accu)
