from unittest import main, TestCase
from patricia import trie

__author__ = 'Florian Leitner'


class Tests(TestCase):
    def testPrefixTrieSetup(self):
        T = trie()
        T['key'] = 'value'
        self.assertTrue('key' in T)
        self.assertEqual('value', T['key'])
        self.assertFalse('keys' in T)
        self.assertFalse('ke' in T)
        self.assertFalse('kex' in T)

    def testPrefixTrieUsage(self):
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

    def testPrefixTrieWithEmptyString(self):
        T = trie()
        T['foo'] = 1
        T[''] = 2
        self.assertTrue('foo' in T)
        self.assertTrue('' in T)
        del T['']
        self.assertRaises(KeyError, T.__getitem__, '')

    def testPrefixTrieIterator(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertListEqual(sorted(['fool', 'ba', 'baz']), sorted(list(T)))
        T[''] = 0
        self.assertEqual(sorted(['', 'fool', 'ba', 'baz']), sorted(list(T)))

    def testPrefixTrieStr(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = "hey's"
        T['fool'] = 1.5
        result = str(T)
        self.assertTrue(result.startswith("<trie{"), result)
        self.assertTrue(result.endswith('}>'), result)
        self.assertTrue("'ba': 2" in result, result)
        self.assertTrue("'baz': \"hey's\"" in result, result)
        self.assertTrue("'fool': 1.5" in result, result)

    def testPrefixTrieIndexOf(self):
        T = trie()
        T['ba'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertEqual(2, T.indexOf('bar'))
        self.assertEqual(4, T.indexOf('fool'))
        self.assertEqual(-1, T.indexOf('fo'))
        self.assertEqual(-1, T.indexOf(''))
        s = 'fools and stuff'
        self.assertEqual(4, T.indexOf(s))
        self.assertEqual(-1, T.indexOf(s[1:]))
        T[''] = 0
        self.assertEqual(0, T.indexOf(''))
        self.assertEqual(3, T.indexOf('bazar'))


    def testPrefixTrieIsPrefix(self):
        T = trie()
        T['bar'] = 2
        T['baz'] = 3
        T['fool'] = 1
        self.assertTrue(T.isPrefix('ba'))
        self.assertFalse(T.isPrefix('fools'))
        self.assertTrue(T.isPrefix(''))

    def testPrefixTriePrefixIter(self):
        T = trie()
        T['b'] = 1
        T['baar'] = 2
        T['baahus'] = 3
        self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.prefixIter('ba'))))
        self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.prefixIter('baa'))))
        self.assertListEqual(sorted(['b', 'baar', 'baahus']), sorted(list(T.prefixIter('b'))))


if __name__ == '__main__':
    main()
