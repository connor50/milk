import nltk
from nltk.tokenize import TweetTokenizer

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives="positive-words.txt", negatives="negative-words.txt"):
        self.positives = set()
        self.negatives = set()

        # loads positive text into positive set.
        textone = open(positives, "r")
        for line in textone:
            self.positives.add(line.rstrip("\n"))
        textone.close()

        # loads negative text into negative set.
        texttwo = open(negatives, "r")
        for line in texttwo:
            self.negatives.add(line.rstrip("\n"))
        texttwo.close()

    def analyze(self, text):
        # initialises count values.
        positivecount = 0
        negativecount = 0

        # tokenises tweets and applies analysis to each token.
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token in self.positives:
                positivecount += 1
            elif token in self.negatives:
                negativecount -= 1
        # returns sum of positive and negative counts of tokens.
        return (negativecount + positivecount)
