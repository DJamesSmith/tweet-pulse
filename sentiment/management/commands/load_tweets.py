# Loads a random sample of Sentiment140 tweets and scores them with VADER.

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from sentiment.analyzer import analyze
from sentiment.models import Tweet

CSV_FILE = settings.BASE_DIR / "data" / "training.1600000.processed.noemoticon.csv"

# Sentiment140 has no header row, so we name the columns ourselves.
COLUMNS = ["target", "ids", "date", "flag", "user", "text"]

# In Sentiment140, 0 means negative and 4 means positive.
REAL_LABELS = {0: "Negative", 4: "Positive"}


class Command(BaseCommand):
    help = "Load and score a random sample of Sentiment140 tweets"

    def add_arguments(self, parser):
        parser.add_argument("--sample", type=int, default=10000)

    def handle(self, *args, **options):
        if not CSV_FILE.exists():
            self.stderr.write(f"File not found: {CSV_FILE}")
            self.stderr.write("Download it from Kaggle and put it in the data folder.")
            return

        self.stdout.write("Reading the CSV file...")
        data = pd.read_csv(CSV_FILE, encoding="latin-1", header=None, names=COLUMNS)

        sample_size = min(options["sample"], len(data))
        data = data.sample(n=sample_size, random_state=42)

        # Remove old dataset tweets so loading twice does not create duplicates.
        Tweet.objects.filter(source="dataset").delete()

        self.stdout.write(f"Scoring {sample_size} tweets...")
        tweets = []
        for row in data.itertuples():
            score, label = analyze(row.text)
            tweets.append(Tweet(
                text=row.text,
                score=score,
                sentiment=label,
                real_label=REAL_LABELS[row.target],
                source="dataset",
            ))

        Tweet.objects.bulk_create(tweets)
        self.stdout.write(self.style.SUCCESS(f"Done! Loaded {len(tweets)} tweets."))