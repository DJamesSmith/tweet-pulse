from django import forms


class AnalyzeForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Type a tweet or any sentence...",
        }))


class UploadForm(forms.Form):
    file = forms.FileField(
        help_text="A CSV with a column named 'text', or a file in the Sentiment140 format. Up to 10,000 rows are read.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".csv"}))