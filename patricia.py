"""
.. py:module:: patricia
   :synopsis: A PATRICIA trie implementation.

.. moduleauthor:: Florian Leitner <florian.leitner@gmail.com>
.. License: Apache License v2 (http://www.apache.org/licenses/LICENSE-2.0.html)
"""

__author__ = 'Florian Leitner'
__version__ = 1

class _NonTerminal(): pass
__NON_TERMINAL__ = _NonTerminal()

# recursive functions

def _count(node):
    "Count the number of terminal nodes in this branch."
    count = 0 if (node._value is __NON_TERMINAL__) else 1
    for child in node._edges.values():
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
    for edge, child in node._edges.items():
        accu.append(edge)
        for key, value in _items(child, accu):
            yield key, value
        accu.pop()

def _values(node):
    "Yield values of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield node._value
    for child in node._edges.values():
        for value in _values(child):
            yield value

class trie():
    """
    A PATRICIA trie implementation for efficient matching of string
    collections on text.

    This class has an (Py2.7+) API nearly equal to dictionaries. The only
    differences are

    Note that deletion is a "half-supported" operation only. The key seems
    "removed", but the trie is not actually changed, only the node state is
    changed from terminal to non-terminal. I.e., if you frequently delete keys,
    the compaction will become fragmented and less efficient. To mitigate this
    effect, make a copy of the trie (using a copy constructor idiom)::

        T = trie(**T)

    Usage Example::

    >>> T = trie(1, key='value', king='kong') # a root value and two pairs
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
    >>> T.value(S[1:]) # remember: the empty root always matches!
    1
    >>> del T[''] # interlude: deleting keys
    >>> T.item(S[9:]) # raise error if no key is a prefix of S
    Traceback (most recent call last):
        ...
    KeyError: 'k'
    >>> # info: the error string above contains the matched path so far
    >>> T.item(S[1:], None) # avoid the error by specifying a default
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
        Any arguments will be used as the value of this node.
        If keyword arguments are given, they initialize a whole branch.
        """
        self._edges = {}
        self._value = __NON_TERMINAL__
        if len(value):
            if len(value) == 1:
                self._value = value[0]
            else:
                self._value = value
        for key, val in keys.items():
            self[key] = val

    def _find(self, path, offset):
        for edge in self._edges:
            if path.startswith(edge, offset):
                return self._edges[edge], offset + len(edge)
        else:
            return None, offset # return None

    def _next(self, path, offset):
        for edge in self._edges:
            if path.startswith(edge, offset):
                return self._edges[edge], offset + len(edge)
        else:
            raise KeyError(path) # raise error

    def _scan(self, string, rval_fun):
        node = self
        idx = 0
        while node is not None:
            if node._value is not __NON_TERMINAL__:
                yield rval_fun(string, idx, node._value)
            node, idx = node._find(string, idx)

    def __setitem__(self, key, value):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            for edge in node._edges:
                # if the whole prefix matches, advance:
                if key.startswith(edge, idx):
                    node = node._edges[edge]
                    idx += len(edge)
                    break
                # check if the prefix could match (part of) s:
                elif edge[0] == key[idx]:
                    # and split on the longest common prefix
                    pos = 1
                    last = max(len(edge), keylen - idx)
                    while pos < last and edge[pos] == key[idx + pos]:
                        pos += 1
                    split = trie()
                    split._edges[edge[pos:]] = node._edges[edge]
                    node._edges[edge[:pos]] = split
                    del node._edges[edge]
                    node = split
                    idx += pos
                    break
            # no common prefix, create a completely new node
            else:
                node._edges[key[idx:]] = trie(value)
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

    def key(self, string, default=__NON_TERMINAL__):
        """
        Return the longest key that is a prefix of `string`.
        Raise a KeyError or return a `default` if no key is found.
        """
        result = self.item(string, default)
        return result[0] if result is not default else result

    def keys(self, string=None):
        "Return all keys (that are a prefix of `string`)."
        if string is None:
            return _keys(self, [])
        else:
            return self._scan(string, (lambda string, idx, value: string[:idx]))

    def value(self, string, default=__NON_TERMINAL__):
        """
        Return the value of the longest key that is a prefix of `string`.
        Raise a KeyError or return a `default` if no key is found.
        """
        result = self.item(string, default)
        return result[1] if result is not default else result

    def values(self, string=None):
        "Return all values (for keys that are a prefix of `string`)."
        if string is None:
            return _values(self)
        else:
            return self._scan(string, (lambda string, idx, value: value))

    def item(self, string, default=__NON_TERMINAL__):
        """
        Return the key, value pair of the longest key that is a prefix of
        `string`.
        Raise a KeyError or return a `default` if no key is found.
        """
        node = self
        strlen = len(string)
        idx = 0
        last = self._value
        while idx < strlen:
            node, idx = node._find(string, idx)
            if node is None:
                break
            elif node._value is not __NON_TERMINAL__:
              last = node._value
        if last is not __NON_TERMINAL__:
            return string[:idx], last
        elif default is not __NON_TERMINAL__:
            return default
        else:
            raise KeyError(string[:idx])

    def items(self, string=None):
        "Return all key, value pairs (for keys that are a prefix of `string`)."
        if string is None:
            return _items(self, [])
        else:
            return self._scan(string, (lambda string, idx, value: (string[:idx], value)))

    def isPrefix(self, string):
        "Return True if any key starts with `string`."
        node = self
        strlen = len(string)
        idx = 0
        while idx < strlen:
            len_left = strlen - idx
            for edge, child in node._edges.items():
                elen = len(edge)
                prefix = edge[:len_left] if (len_left < elen) else edge
                if string.startswith(prefix, idx):
                    node = child
                    idx += elen
                    break
            else:
                return False
        return True

    def iter(self, prefix):
        "Return an iterator over all keys that start with `prefix`."
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
            for edge in node._edges:
                if edge.startswith(remainder):
                    node = node._edges[edge]
                    accu.append(edge[len(remainder):])
                    break
            else:
                return iter([])
        return _keys(node, accu)
