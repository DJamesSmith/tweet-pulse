from django.contrib import admin

from .models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ["text", "sentiment", "score", "real_label", "source"]
    list_filter = ["sentiment", "real_label", "source"]
    search_fields = ["text"]