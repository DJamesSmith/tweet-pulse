# TweetPulse: Twitter Sentiment Analysis with Django & NLTK VADER

A beginner-friendly Django web app that sorts tweets into **Positive**, **Negative** or **Neutral** using NLTK's **VADER** sentiment analyzer. It is trained on nothing and needs no machine learning setup: VADER is a rule-based analyzer built for short social media text.

The project uses the [Sentiment140](https://www.kaggle.com/datasets/kazanova/sentiment140) dataset (1.6 million labelled tweets) and goes one step further than most sentiment demos: it **checks how often VADER is actually right** by comparing its predictions with the dataset's real labels.

The code is deliberately kept small and easy to read, so it works well as a learning project.

---

## Features

| Feature | What it does |
|---|---|
| **Dataset import** | Loads a random sample of Sentiment140 tweets into the database with one command. |
| **Sentiment scoring** | Scores every tweet with VADER and labels it Positive, Negative or Neutral. |
| **Accuracy evaluation** | Compares VADER's predictions with the real labels and shows accuracy, a confusion matrix and the tweets it got wrong. |
| **Live analyzer** | Type any sentence and instantly see its score, its label and which words pushed the score up or down. |
| **Dashboard charts** | A pie chart of the sentiment split and bar charts of the most common words in each category (Chart.js). |
| **CSV upload & export** | Upload your own CSV of tweets, get them scored, and download the results as a CSV. |

---

## How the sentiment is decided

VADER gives each tweet a **compound score** from **-1** (most negative) to **+1** (most positive).

| Compound score | Label |
|---|---|
| 0.05 or higher | Positive |
| -0.05 or lower | Negative |
| between -0.05 and 0.05 | Neutral |

### A note on accuracy

Sentiment140 only labels tweets as **negative (0)** or **positive (4)**. It has no neutral tweets. Because of that, the accuracy page reports two things:

- **Accuracy** on the tweets VADER labelled Positive or Negative
- **How many** tweets VADER labelled Neutral (these are shown separately, not counted as right or wrong)

---

## Tech stack

- Python 3.10+
- Django 5
- NLTK (VADER lexicon)
- pandas (reading the CSV)
- SQLite (default Django database)
- Chart.js (charts, loaded from a CDN)
- Bootstrap 5 (styling, loaded from a CDN)

---

## Project structure

```
tweet-pulse/
├── manage.py
├── requirements.txt
├── data/                          # put the Kaggle CSV here (not committed)
├── tweet-pulse/                    # Django project settings
│   ├── settings.py
│   └── urls.py
└── sentiment/                     # the main app
    ├── models.py                  # Tweet model
    ├── analyzer.py                # all VADER logic in one place
    ├── views.py                   # dashboard, analyzer, accuracy, upload, export
    ├── urls.py
    ├── forms.py
    ├── management/commands/
    │   └── load_tweets.py         # imports and scores the dataset
    └── templates/sentiment/
```

---

## Getting started

### 1. Clone the project and create a virtual environment

```bash
git clone https://github.com/<your-username>/tweet-pulse.git
cd tweet-pulse
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install the requirements

```bash
pip install -r requirements.txt
```

### 3. Download the VADER lexicon

```bash
python -m nltk.downloader vader_lexicon
```

### 4. Download the dataset

1. Go to [Sentiment140 on Kaggle](https://www.kaggle.com/datasets/kazanova/sentiment140) and download it.
2. Unzip it and place `training.1600000.processed.noemoticon.csv` inside the `data/` folder.

The file has **no header row** and uses **latin-1** encoding. Its six columns are:

| Column | Meaning |
|---|---|
| target | Real sentiment: 0 = negative, 4 = positive |
| ids | Tweet ID |
| date | Date of the tweet |
| flag | Search query (always `NO_QUERY`) |
| user | Username of the author |
| text | The tweet itself |

### 5. Set up the database

```bash
python manage.py migrate
```

### 6. Import and score the tweets

The full dataset has 1.6 million rows, so the command loads a random sample. 10,000 tweets is a good size for a quick start:

```bash
python manage.py load_tweets --sample 10000
```

### 7. Run the server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Pages

| URL | Page |
|---|---|
| `/` | Dashboard with charts |
| `/analyze/` | Live analyzer |
| `/accuracy/` | VADER accuracy evaluation |
| `/tweets/` | Browse scored tweets, filter by sentiment |
| `/upload/` | Upload your own CSV |
| `/export/` | Download scored tweets as CSV |

### Uploading your own CSV

Your file needs a column named **`text`**. Every other column is ignored. Example:

```csv
text
I love this new phone!
Worst service ever, never coming back.
The meeting is at 3pm.
```

---

## Known limits of VADER

VADER works from a fixed list of words and rules, so it struggles with:

- **Sarcasm:** "Oh great, another Monday" reads as positive.
- **Slang and misspellings** it has never seen.
- **Context:** it scores words, not meaning.

The accuracy page shows real examples of these mistakes from the dataset.

---

## Dataset citation

Go, A., Bhayani, R. and Huang, L. (2009). *Twitter Sentiment Classification using Distant Supervision.* CS224N Project Report, Stanford.

Dataset: [Sentiment140 on Kaggle](https://www.kaggle.com/datasets/kazanova/sentiment140)

## VADER citation

Hutto, C.J. and Gilbert, E.E. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.* Eighth International Conference on Weblogs and Social Media (ICWSM-14).

---

## Author

**Dion James Smith**, Software Engineer