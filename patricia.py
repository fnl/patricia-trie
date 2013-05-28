"""
.. py:module:: patricia
   :synopsis: A PATRICIA trie implementation.

.. moduleauthor:: Florian Leitner <florian.leitner@gmail.com>
.. License: Apache License v2 (http://www.apache.org/licenses/LICENSE-2.0.html)
"""

from io import StringIO

class _NonTerminal(): pass

NON_TERMINAL = _NonTerminal()

class trie():
    """
    A PATRICIA trie implementation for efficient matching of string
    collections.

    Usage Example:

    >>> T = trie() # add a few values
    >>> T['key'] = 'value'
    >>> T['kong'] = 'king'
    >>> T[''] = 1
    >>> '' in T # check if the value exits (note: empty node!)
    True
    >>> 'king' in T
    False
    >>> T['kong'] # get an exact value
    'king'
    >>> T['king'] # errors for non-existing keys
    Traceback (most recent call last):
        ...
    KeyError: 'king'
    >>> len(T) # count the leafs in the tree
    3
    >>> s = 'keys and other stuff'
    >>> T.indexOf(s) # report the (longest) offset if any key is a prefix of s
    3
    >>> T.indexOf(s[1:]) # problem: the empty node always matches!
    0
    >>> del T[''] # it is also fine to delete keys
    >>> T.indexOf(s[1:]) # now reports -1 as index if no key is a prefix of s
    -1
    >>> T.isPrefix('k') # ... or check if a string is a prefix of any key
    True
    >>> T.isPrefix('king')
    False
    >>> sorted(list(T.prefixIter('k'))) # and get all keys matching a prefix
    ['key', 'kong']
    """

    def __init__(self, value=NON_TERMINAL, edges=None):
        self.edges = {} if edges is None else edges
        self.value = value

    @staticmethod
    def __recurse(target, node, suffix, idx):
        for prefix in node.edges:
            if suffix.startswith(prefix, idx):
                return target(node.edges[prefix], suffix, idx + len(prefix))
        raise KeyError(suffix)

    def __setitem__(self, key, value):
        trie._setRecursion(self, key, 0, value)

    @staticmethod
    def _setRecursion(node, s, idx, value):
        if len(s) == idx:
            node.value = value
        else:
            for prefix in node.edges:
                # if the whole prefix matches, recurse:
                if s.startswith(prefix, idx):
                    return trie._setRecursion(
                        node.edges[prefix], s, idx + len(prefix), value
                    )
                elif prefix[0] == s[idx]:
                    # find the longest common prefix:
                    pos = 1
                    while prefix[pos] == s[idx + pos]:
                        pos += 1
                    split = trie()
                    split.edges[prefix[pos:]] = node.edges[prefix]
                    node.edges[prefix[:pos]] = split
                    del node.edges[prefix]
                    return trie._setRecursion(split, s, idx + pos, value)
                # no common prefix, create a completely new node
            node.edges[s[idx:]] = trie(value)

    def __getitem__(self, item):
        return trie._getRecursion(self, item, 0)

    @staticmethod
    def _getRecursion(node, s, idx):
        if len(s) == idx:
            if node.value is NON_TERMINAL:
                raise KeyError(s)
            else:
                return node.value
        else:
            return trie.__recurse(node._getRecursion, node, s, idx)

    def __contains__(self, item):
        return trie._containsRecursion(self, item, 0)

    @staticmethod
    def _containsRecursion(node, s, idx):
        if len(s) == idx:
            if node.value is NON_TERMINAL:
                return False
            else:
                return True
        else:
            try:
                return trie.__recurse(
                    trie._containsRecursion, node, s, idx
                )
            except KeyError:
                return False

    def __delitem__(self, key):
        trie._delRecursion(self, key, 0)

    @staticmethod
    def _delRecursion(node, s, idx):
        if len(s) == idx:
            if node.value is NON_TERMINAL:
                raise KeyError(s)
            else:
                node.value = NON_TERMINAL
        else:
            trie.__recurse(node._delRecursion, node, s, idx)

    def __iter__(self):
        for k in trie._iterRecursion(self, StringIO()):
            yield k.getvalue()

    def __len__(self):
        return sum(trie._countRecursion(self))

    @staticmethod
    def _countRecursion(node):
        if node.value is not NON_TERMINAL:
            yield 1
        for child in node.edges.values():
            for i in trie._countRecursion(child):
                yield i

    @staticmethod
    def _iterRecursion(node, accu):
        offset = accu.tell()
        if node.value is not NON_TERMINAL:
            yield accu
        for prefix in node.edges:
            accu.write(prefix)
            for key in trie._iterRecursion(node.edges[prefix], accu):
                yield key
            accu.seek(offset)
            accu.truncate()

    def __str__(self):
        string = StringIO()
        string.write('<trie{')
        first = True
        for k in self:
            if first: first = False
            else: string.write(', ')
            string.write(repr(k))
            string.write(': ')
            string.write(repr(self[k]))
        string.write('}>')
        return string.getvalue()

    def indexOf(self, string):
        """
        Returns the end of the longest matching key at the beginning of the
        string or -1 if no match was found.
        """
        return trie._indexRecursion(self, string, 0)

    @staticmethod
    def _indexRecursion(node, s, idx):
        if len(s) == idx:
            return trie.__indexCheck(node.value, idx)
        else:
            try:
                return trie.__recurse(
                    trie._indexRecursion, node, s, idx
                )
            except KeyError:
                return trie.__indexCheck(node.value, idx)

    @staticmethod
    def __indexCheck(value, idx):
        if value is NON_TERMINAL:
            if idx == 0:
                return -1
            else:
                raise KeyError()
        else:
            return idx

    def isPrefix(self, string):
        """
        Returns True if the string is a prefix of any of the keys in the
        trie, False otherwise.
        """
        return trie._prefixRecursion(self, string, 0, len(string))

    def prefixIter(self, prefix):
        """
        Return an iterator over all keys that have the given prefix.
        """
        return trie._prefixIterRecursion(self, prefix, 0, len(prefix))

    @staticmethod
    def _prefixIterRecursion(node, s, idx, slen):
        if slen == idx:
            accu = StringIO()
            accu.write(s)
            for k in trie._iterRecursion(node, accu):
                yield k.getvalue()
        else:
            for prefix in node.edges:
                if s.startswith(prefix, idx):
                    for k in trie._prefixIterRecursion(
                            node.edges[prefix], s, idx + len(prefix), slen
                        ):
                        yield k
                elif slen < idx + len(prefix):
                    p = prefix[:slen-idx]
                    if s.startswith(p, idx):
                        accu = StringIO()
                        accu.write(s[:idx])
                        accu.write(prefix)
                        for k in trie._iterRecursion(node.edges[prefix], accu):
                            yield k.getvalue()

    @staticmethod
    def _prefixRecursion(node, s, idx, slen):
        if slen == idx:
            return True
        else:
            for prefix in node.edges:
                p = prefix[:slen-idx]
                if s.startswith(p, idx):
                    return trie._prefixRecursion(
                        node.edges[prefix], s, idx + len(p), slen
                    )
            return False

