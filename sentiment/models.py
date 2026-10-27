from django.db import models


class Tweet(models.Model):
    SENTIMENT_CHOICES = [
        ("Positive", "Positive"),
        ("Negative", "Negative"),
        ("Neutral", "Neutral"),
    ]
    SOURCE_CHOICES = [
        ("dataset", "Sentiment140 dataset"),
        ("upload", "Uploaded CSV"),
    ]

    text = models.TextField()
    score = models.FloatField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)

    # The real label from Sentiment140 (Positive or Negative). Uploaded tweets have no real label, so it stays empty.
    real_label = models.CharField(max_length=10, blank=True)

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="dataset")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sentiment}: {self.text[:50]}"