patricia-trie
=============

A pure Python 2.7+ implementation of a PATRICIA trie for effcient matching
of string collections on text.

Note that you probably first want to have a look at `marisa-trie`_ or its
`PyPi package <https://github.com/kmike/marisa-trie/>`_ before using this.

`patricia-trie` has a clean API that imitates the dict() API and works with Py3k.

Installation
------------

::

  pip install patricia-trie

Usage
-----

::

    >>> from patricia import trie
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

Note that deletion is a "half-supported" operation only. The key seems
"removed", but the trie is not actually changed, only the node state is
changed from terminal to non-terminal. I.e., if you frequently delete keys,
the compaction will become fragmented and less efficient. To mitigate this
effect, make a copy of the trie (using a copy constructor idiom)::

    T = trie(**T)

Copyright
---------

Copyright 2013, Florian Leitner, All rights reserved.

License
-------

`Apache License v2 <http://www.apache.org/licenses/LICENSE-2.0.html>`_

.. _marisa-trie: https://code.google.com/p/marisa-trie/
.. _patricia-trie: https://www.github.com/fnl/patricia-trie/
