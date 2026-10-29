import csv
import io

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, F
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .analyzer import analyze, analyze_in_detail, top_words
from .forms import AnalyzeForm, UploadForm
from .models import Tweet

LABELS = ["Positive", "Negative", "Neutral"]


def dashboard(request):
    tweets = Tweet.objects.all()

    # How many tweets are in each category.
    counts = [tweets.filter(sentiment=label).count() for label in LABELS]

    # Most common words in positive and negative tweets.
    positive_words = top_words(tweets.filter(sentiment="Positive").values_list("text", flat=True))
    negative_words = top_words(tweets.filter(sentiment="Negative").values_list("text", flat=True))

    # This dictionary is passed to Chart.js in the template.
    chart_data = {
        "labels": LABELS,
        "counts": counts,
        "positive_words": [word for word, count in positive_words],
        "positive_counts": [count for word, count in positive_words],
        "negative_words": [word for word, count in negative_words],
        "negative_counts": [count for word, count in negative_words],
    }

    context = {
        "total": tweets.count(),
        "positive": counts[0],
        "negative": counts[1],
        "neutral": counts[2],
        "average_score": tweets.aggregate(Avg("score"))["score__avg"] or 0,
        "chart_data": chart_data,
    }
    return render(request, "sentiment/dashboard.html", context)


def analyze_text(request):
    result = None
    form = AnalyzeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        result = analyze_in_detail(form.cleaned_data["text"])

    return render(request, "sentiment/analyze.html", {"form": form, "result": result})


def accuracy(request):
    # Only dataset tweets have a real label to compare against.
    tweets = Tweet.objects.filter(source="dataset")

    # Confusion matrix: one row for each real label,
    # one column for each label VADER predicted.
    matrix = []
    for real in ["Positive", "Negative"]:
        row = {"real": real}
        for predicted in LABELS:
            row[predicted] = tweets.filter(real_label=real, sentiment=predicted).count()
        matrix.append(row)

    # Sentiment140 has no neutral tweets, so Neutral predictions
    # are counted separately and left out of the accuracy.
    neutral_count = tweets.filter(sentiment="Neutral").count()
    decided = tweets.exclude(sentiment="Neutral")
    correct = decided.filter(sentiment=F("real_label")).count()
    accuracy_percent = correct / decided.count() * 100 if decided.exists() else 0

    # A few random tweets VADER got wrong.
    wrong_tweets = decided.exclude(sentiment=F("real_label")).order_by("?")[:10]

    context = {
        "total": tweets.count(),
        "decided": decided.count(),
        "correct": correct,
        "accuracy": accuracy_percent,
        "neutral_count": neutral_count,
        "matrix": matrix,
        "wrong_tweets": wrong_tweets,
    }
    return render(request, "sentiment/accuracy.html", context)


def filtered_tweets(request):
    """Shared by the tweet list and the export, so both use the same filters."""
    tweets = Tweet.objects.all().order_by("-id")

    sentiment = request.GET.get("sentiment", "")
    source = request.GET.get("source", "")
    if sentiment:
        tweets = tweets.filter(sentiment=sentiment)
    if source:
        tweets = tweets.filter(source=source)

    return tweets, sentiment, source


def tweet_list(request):
    tweets, sentiment, source = filtered_tweets(request)

    paginator = Paginator(tweets, 25)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "page": page,
        "total": tweets.count(),
        "sentiment": sentiment,
        "source": source,
        "labels": LABELS,
        "query": request.GET.urlencode(),
    }
    return render(request, "sentiment/tweet_list.html", context)


MAX_UPLOAD_ROWS = 10000
SENTIMENT140_COLUMNS = ["target", "ids", "date", "flag", "user", "text"]


def read_uploaded_csv(file):
    """
    Read an uploaded CSV and return a table with a 'text' column.
    Returns None if no tweet column can be found.
    """
    # Read the file into memory once, so we can parse it twice if needed.
    content = file.read()

    data = pd.read_csv(io.BytesIO(content), encoding_errors="replace", nrows=MAX_UPLOAD_ROWS)

    # "Text", " text " and "TEXT" should all count as "text".
    data.columns = [str(column).strip().lower() for column in data.columns]
    if "text" in data.columns:
        return data

    # The Sentiment140 file has no header row and 6 columns,
    # so read it again and name the columns ourselves.
    if len(data.columns) == 6:
        return pd.read_csv(io.BytesIO(content), encoding="latin-1", header=None,
                           names=SENTIMENT140_COLUMNS, nrows=MAX_UPLOAD_ROWS)

    return None


def upload_csv(request):
    form = UploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        try:
            data = read_uploaded_csv(request.FILES["file"])
        except Exception:
            messages.error(request, "Could not read that file. Please upload a valid CSV.")
            return redirect("upload")

        if data is None:
            messages.error(request, "Your CSV needs a column named 'text', or must be in the Sentiment140 format.")
            return redirect("upload")

        tweets = []
        for text in data["text"].dropna():
            score, label = analyze(text)
            tweets.append(Tweet(text=text, score=score, sentiment=label, source="upload"))

        Tweet.objects.bulk_create(tweets)
        messages.success(request, f"Scored and saved {len(tweets)} tweets.")
        return redirect("/tweets/?source=upload")

    return render(request, "sentiment/upload.html", {"form": form})


def export_csv(request):
    tweets, sentiment, source = filtered_tweets(request)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="scored_tweets.csv"'

    writer = csv.writer(response)
    writer.writerow(["text", "score", "sentiment", "real_label", "source"])
    for tweet in tweets:
        writer.writerow([tweet.text, tweet.score, tweet.sentiment, tweet.real_label, tweet.source])

    return response