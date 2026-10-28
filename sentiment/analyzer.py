# All the NLTK sentiment logic lives in this one file.
# VADER gives every text a "compound" score from -1 (very negative) to +1 (very positive). We turn that score into a label:

#     score >= 0.05   -> Positive
#     score <= -0.05  -> Negative
#     anything else   -> Neutral

import html
import re
from collections import Counter

from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Create the analyzer once and reuse it everywhere.
vader = SentimentIntensityAnalyzer()

STOP_WORDS = set(stopwords.words("english"))


# Remove the parts of a tweet that carry no sentiment.
def clean_text(text):
    text = html.unescape(str(text))                         # "&amp;" -> "&"
    text = re.sub(r"http\S+|www\.\S+", "", text)            # links
    text = re.sub(r"@\w+", "", text)                        # @mentions
    text = text.replace("#", "")                            # keep the hashtag word, drop "#"
    return text.strip()


# Turn a compound score into Positive, Negative or Neutral.
def get_label(score):
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


# Return (score, label) for a piece of text.
def analyze(text):
    score = vader.polarity_scores(clean_text(text))["compound"]
    return score, get_label(score)


# Used by the live analyzer page.
# Returns the full VADER scores plus the words that moved the score.
def analyze_in_detail(text):
    cleaned = clean_text(text)
    scores = vader.polarity_scores(cleaned)

    # Look up each word in VADER's word list (its "lexicon").
    word_scores = []
    for word in cleaned.lower().split():
        word = word.strip(".,!?;:\"'()")
        if word in vader.lexicon:
            word_scores.append({"word": word, "value": vader.lexicon[word]})

    return {
        "score": scores["compound"],
        "label": get_label(scores["compound"]),
        "positive": round(scores["pos"] * 100),
        "neutral": round(scores["neu"] * 100),
        "negative": round(scores["neg"] * 100),
        "words": word_scores,
    }


# Count the most common meaningful words in a list of texts.
def top_words(texts, how_many=10):
    counter = Counter()
    for text in texts:
        for word in re.findall(r"[a-z']+", clean_text(text).lower()):
            if len(word) > 2 and word not in STOP_WORDS:
                counter[word] += 1
    return counter.most_common(how_many)