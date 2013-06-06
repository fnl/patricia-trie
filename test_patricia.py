"""
.. py:module:: test_patricia
   :synopsis: Test cases for the PATRICIA trie implementation.

.. moduleauthor:: Florian Leitner <florian.leitner@gmail.com>
.. License: Apache License v2 (http://www.apache.org/licenses/LICENSE-2.0.html)
"""
from unittest import main, TestCase
from patricia import trie, _NonTerminal

__author__ = 'Florian Leitner'
__version__ = 1

class Tests(TestCase):
    def testInitContains(self):
        T = trie()
        T['key'] = 'value'
        T = trie(**T)
        self.assertTrue('key' in T)
        self.assertFalse('keys' in T)
        self.assertFalse('ke' in T)
        self.assertFalse('kex' in T)

    def testSetGetDel(self):
        T = trie()
        T['foo'] = 1
        T['bar'] = 2
        T['baz'] = 3
        self.assertTrue('foo' in T)
        self.assertTrue('bar' in T)
        self.assertTrue('baz' in T)
        self.assertEqual(T['foo'], 1)
        self.assertEqual(T['bar'], 2)
        self.assertEqual(T['baz'], 3)
        self.assertRaises(KeyError, T.__getitem__, 'ba')
        self.assertRaises(KeyError, T.__getitem__, 'fool')
        del T['bar']
        self.assertRaises(KeyError, T.__getitem__, 'bar')
        self.assertEqual(T['baz'], 3)

    def testEmptyStringKey(self):
        T = trie()
        T['foo'] = 1
        T[''] = 2
        self.assertTrue('foo' in T)
        self.assertTrue('' in T)
        del T['']
        self.assertRaises(KeyError, T.__getitem__, '')

    def testIterator(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertListEqual(sorted(['fool', 'ba', 'baz']), sorted(list(T)))
        T[''] = 0
        self.assertEqual(sorted(['', 'fool', 'ba', 'baz']), sorted(list(T)))

    def testValues(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = "hey's"
        T['fool'] = 1.5
        self.assertListEqual(sorted(["2", "hey's", "1.5"]), sorted([str(v) for v in T.values()]))

    def testStrRepr(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = "hey's"
        T['fool'] = 1.5
        result = repr(T)
        self.assertTrue(result.startswith("trie({"), result)
        self.assertTrue(result.endswith('})'), result)
        self.assertTrue("'ba': 2" in result, result)
        self.assertTrue("'baz': \"hey's\"" in result, result)
        self.assertTrue("'fool': 1.5" in result, result)

    def testGetItems(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertEqual(('ba', 2), T.item('bar'))
        self.assertEqual(1, T.value('fool'))
        self.assertRaises(KeyError, T.key, 'foo')
        T[''] = 0
        self.assertEqual(('', 0), T.item(''))
        self.assertEqual('', T.key('foo'))

    def testFakeDefault(self):
        T = trie()
        fake = _NonTerminal()
        self.assertEqual(fake, T.key('foo', default=fake))

    def testLongRootValue(self):
        T = trie(1, 2)
        self.assertEqual((1, 2), T[''])

    def testIterItems(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertListEqual(['ba', 'baz'], list(T.keys('bazar')))
        self.assertListEqual([('fool', 1)], list(T.items('fools')))
        self.assertListEqual([], list(T.values('others')))

    def testIsPrefix(self):
        T = trie()
        T['bar'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertTrue(T.isPrefix('ba'))
        self.assertFalse(T.isPrefix('fools'))
        self.assertTrue(T.isPrefix(''))

    def testIterPrefix(self):
        T = trie()
        T['b'] = 1
        T['baar'] = 2
        T['baahus'] = 3
        self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.iter('ba'))))
        self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.iter('baa'))))
        self.assertListEqual(sorted(['b', 'baar', 'baahus']), sorted(list(T.iter('b'))))
        self.assertListEqual(sorted([]), sorted(list(T.iter('others'))))

    def testOffsetMatching(self):
        T = trie()
        T['foo'] = 1
        T['baar'] = 2
        T['baarhus'] = 3
        T['bazar'] = 4
        txt = 'The fool baal baarhus in the bazar!'
        keys = []
        values = []
        items = []
        for i in range(len(txt)):
            values.extend(T.values(txt, i))
        for i in range(len(txt)):
            keys.extend(T.keys(txt, i))
        for i in range(len(txt)):
            items.extend(T.items(txt, i))
        self.assertListEqual([1, 2, 3, 4], values)
        self.assertListEqual(['foo', 'baar', 'baarhus', 'bazar'], keys)
        self.assertListEqual([('foo', 1), ('baar', 2), ('baarhus', 3), ('bazar', 4)], items)

    def testKeyPresenceOnly(self):
        T = trie()
        T['foo'] = True
        T['baar'] = True
        T['baarhus'] = True
        T['bazar'] = True
        txt = 'The fool baal baarhus in the bazar!'
        presence = [4, 14, 29]
        for i in range(len(txt)):
            if T.value(txt, False, i):
                self.assertTrue(i in presence,
                                '{} {} "{}"'.format(str(presence), i, txt[i:]))
                presence.remove(i)
        self.assertEqual(0, len(presence), str(presence))

if __name__ == '__main__':
    main()
