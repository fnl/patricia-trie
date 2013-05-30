patricia-trie
=============

A pure Python 2.7+ implementation of a PATRICIA trie.

Note that you probably first want to have a look at `marisa-trie`_ or its
`PyPi package <https://github.com/kmike/marisa-trie/>`_ before using this.

This implementation is more efficient than PyTrie v0.1, has a clean
API that imitates the dict() API, and works with Py3k.

Installation
------------

::

  pip install patricia-trie

Usage
-----

::

  from patricia import trie
  help(trie)

Copyright
---------

Copyright 2013, Florian Leitner, All rights reserved.

License
-------

`Apache License v2 <http://www.apache.org/licenses/LICENSE-2.0.html>`_

.. _marisa-trie: https://code.google.com/p/marisa-trie/
.. _patricia-trie: https://www.github.com/fnl/patricia-trie/
