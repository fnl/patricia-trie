from marisa_trie import Trie

TEXT = """
On the seventh of November, the two boys went on a sixty day long trip to
twenty-three different capitals of the twelve continents.
Their eighteen pets were, together, two-hundred-and-fourteen years old.
    """

S1 = (1, TEXT.index('.') + 1)
S2 = (S1[1] + 1, TEXT.rindex('.') + 1)


def test():
    # 1. build a trie
    d = dict(zero=0, one=1, two=2, three=3, four=4, five=5, six=6, seven=7,
             eight=8, nine=9, ten=10, eleven=11, twelve=12, thirteen=13,
             fourteen=10, fifteen=15, sixteen=16, seventeen=17, eighteen=18,
             nineteen=19, twenty=20, thirty=30, fourty=40, fifty=50,
             sixty=60, seventy=70, eighty=80, ninety=90,
             hundred=100)
    t = Trie(list(d.keys()))

    # 2. scan 2000 "sentences" with it
    for _ in range(1000):
    # scanning for the longest matches only in sentence 1
        i = S1[0]
        #print(TEXT[i:S1[1]])
        while i < S1[1]:
            pfx = list(t.prefixes(TEXT[i:S1[1]]))
            if pfx:
                k = pfx[-1]
                #print(d[k])
                i += len(k)
            else:
                i += 1

        # scanning for all matches in sentence 2
        i = S2[0]
        #print(TEXT[i:S2[1]])
        s = 0
        while i < S2[1]:
            for k in t.prefixes(TEXT[i:S2[1]]):
                #print(k)
                s += d[k]
            i += 1
        if s != 142:
            raise RuntimeError(str(s))

    # 3. make a real list of all keys in the trie
    if 'nine' not in list(t.iterkeys()):
        raise RuntimeError(str(list(t.iterkeys())))

if __name__ == '__main__':
    import timeit
    # 4. do that whole thing 3x10 times over and report the results
    print(timeit.repeat("test()", "from __main__ import test", number=10))
