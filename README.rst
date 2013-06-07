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

History
-------

1. Initial release package.
2. Full documentation and corrections.
3. Added optional keyword parameters to indicate an offset ``start`` when
   scanning a string with the methods key(), keys(), item(), items(), value(),
   and values(), so it is not necessary to slice strings for each scan::

       >>> # Old usage to scan 'string' in 'the string' was:
       >>> T.keys('the string'[4:])
       >>> # With the new optional keyword parameter:
       >>> T.keys('the string', start=4)

4. **Important API change**: item() now returns key, value pairs even when a
   default value is given, using ``None`` as the "key"::

       >>> # Old behaviour was:
       >>> T.item('string', default=False)
       False
       >>> # While now, the same call produces:
       >>> T.item('string', default=False)
       None, False

   Other updates: Switched from using dictionaries to two-tuple lists
   internally (thanks to Pedro Gaio for the suggestion!) to improve the
   overall performance a bit (about 20% faster on simple tests).
5. *Bugfix*: When splitting edges while adding a new key that is shorter than
   the current edge, a index error would have occurred.
6. Added optional keyword parameter ``end`` to the methods key(), keys(),
   item(), items(), value(), and values(), so it is not necessary to scan
   within a window::

       T.key('string', start=2, end=3, default=None)
       T.keys('string', start=2, end=3)

Copyright
---------

Copyright 2013, Florian Leitner, All rights reserved.

License
-------

`Apache License v2 <http://www.apache.org/licenses/LICENSE-2.0.html>`_

.. _marisa-trie: https://code.google.com/p/marisa-trie/
.. _patricia-trie: https://www.github.com/fnl/patricia-trie/
