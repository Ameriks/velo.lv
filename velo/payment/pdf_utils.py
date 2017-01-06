from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
import math


def split_word_in_eq(word, times):
    wlen = len(word)
    if wlen < times or times == 0:
        yield word
    else:
        m = int(wlen / times)
        for i in range(0, int(m) * times, int(m)):
            word[i:] if i+m+m > wlen else word[i:i+m]


class BreakingParagraph(Paragraph):
    def breakLines(self, width):
        for n in range(0, len(self.frags)):
            words = self.frags[n].text.split(' ')
            for nn in range(0, len(words)):
                wordWidth = pdfmetrics.stringWidth(words[nn], self.frags[n].fontName, self.frags[n].fontSize, self.encoding)
                w = wordWidth / width[0]
                if w > 1:
                    words[nn] = '\n'.join((split_word_in_eq(words[nn], int(math.ceil(w)))))

            self.frags[n].text = ' '.join(words)
        return Paragraph.breakLines(self, width)
