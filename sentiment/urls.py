from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analyze/", views.analyze_text, name="analyze"),
    path("accuracy/", views.accuracy, name="accuracy"),
    path("tweets/", views.tweet_list, name="tweet_list"),
    path("upload/", views.upload_csv, name="upload"),
    path("export/", views.export_csv, name="export"),
]