# -*- coding: utf-8 -*-

"""Module provides function num_to_text which converts numberic value to lavian
language string.

>>> num_to_text(12)
u'divpadsmit'

>>> num_to_text(152)
u'viens simts piecdesmit divi'
"""

__all__ = ["num_to_text"]

ZERO = u"nulle"

DIGIT = [
    [u"viens", u"vien"],
    [u"divi", u"div"],
    [u"trīs", u"trīs"],
    [u"četri", u"četr"],
    [u"pieci", u"piec"],
    [u"seši", u"seš"],
    [u"septiņi", u"septiņ"],
    [u"astoņi", u"astoņ"],
    [u"deviņi", u"deviņ"],
]

ORDER = [
    [10, u"padsmit", u"desmit"],
    [100, u"simts", u"simti"],
    [1000, u"tūkstotis", u"tūkstoši"],
    [1000000, u"miljons", u"miljoni"],
    [1000000000, u"miljards", u"miljardi"],
]

MAX_NUM = 999999999999

def _num_to_text(i, c, n):
    """Palīgfunkcija, kas atgriež kārtu kā vārdu. "divi miljoni", "divdesmit",
    "trīs", "vienpadsmit" etc.

    i: Kārtas index. desmiti, simti, tūkstoši, miljardi.
    n: Atlikušais skaitlis.
    c: Kārtu skaits.
    """

    if i == 0: # desmiti
        if 1 < c < 10: # desmiti
            w = []
            if c != 0:
                w.append("".join([DIGIT[c - 1][1], ORDER[i][2]]))
            else:
                w.append(ORDER[i][2])

            if n != 0:
                w.append(" ")
                w.append(DIGIT[n - 1][0])

            return "".join(w)
        elif c == 1: # padsmiti
            if n != 0:
                return "".join([DIGIT[n - 1][1], ORDER[i][1]])
            else:
                return ORDER[i][2]
        else: # vieni
            if n > 0:
                return DIGIT[n - 1][0]
    else: # simti un vairāk
        if c <= 0:
            return
        elif c == 0:
            return ORDER[i][1]
        elif c == 1:
            return "".join([DIGIT[c - 1][0], " ", ORDER[i][1]])
        elif 1 < c < 10:
            return "".join([DIGIT[c - 1][0], " ", ORDER[i][2]])
        elif c >= 10:
            w = num_to_text(c)
            c_str = str(c)
            if len(c_str) > 1 and c_str[-2:] == "11":
                return " ".join([w, ORDER[i][2]])
            elif c_str[-1] == "1":
                return " ".join([w, ORDER[i][1]])
            else:
                return " ".join([w, ORDER[i][2]])

def num_to_text(n):
    """Pārveido skaitli par tekstu. 35 -- trīsdesmit pieci, 11 -- vienpadsmit.
    n: Nenegatīvs skaitlis, ne lielāks par 999999999999.

    >>> num_to_text(1)
    u'viens'

    >>> num_to_text(34)
    u'tr\u012bsdesmit \u010detri'

    >>> num_to_text(1021)
    u'viens t\u016bkstotis divdesmit viens'

    >>> num_to_text(10211)
    u'desmit t\u016bksto\u0161i divi simti vienpadsmit'

    >>> num_to_text(111201)
    u'viens simts vienpadsmit t\u016bksto\u0161i divi simti viens'

    >>> num_to_text(0)
    u'nulle'
    """

    if not isinstance(n, int):
        raise Exception("Not an integer")

    if n < 0:
        raise Exception("Negative number")
    elif n > MAX_NUM:
        raise Exception("Number too large")

    text = []
    if n == 0:
        return ZERO
    elif 1 <= n <= 9:
        text.append(DIGIT[n - 1][0])
    else:
        for i in range(len(ORDER) - 1, -1, -1):
            c = n // ORDER[i][0]
            n -= c * ORDER[i][0]
            w = _num_to_text(i, c, n)
            if w is not None:
                assert isinstance(w, str)
                text.append(w)

    val = " ".join(text).strip()
    assert isinstance(val, str)
    return val

if __name__ == "__main__":
    import doctest
    doctest.testmod()
