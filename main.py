from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
from nltk import tokenize
from googletrans import Translator
from flask import Flask, request, jsonify
from celery import Celery

translator = Translator()
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://jdv:jdv@localhost:5672/v_host'


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/')
def health_check():
    return 'Translation Service is up.'


@app.route('/detect-sentiment', methods=['POST'])
def sentiment():
    form = request.form
    text = form['text']
    return _sentiment(text)


@celery.task
def _sentiment(text):
    sid = SentimentIntensityAnalyzer()
    sentiment_score = sid.polarity_scores(text)
    return sentiment_score


@app.route('/synonyms', methods=['POST'])
def synonyms():
    form = request.form
    text = form['text']
    return _synonyms(text)


@celery.task
def _synonyms(text):
    synset = wn.synsets(text)
    return str(synset[0].hyponyms())


@app.route('/detect-lang', methods=['POST'])
def detect():
    form = request.form
    text = form['text']
    return _detect(text)


@celery.task
def _detect(text):
    lang_detected = translator.detect(text)
    return lang_detected.lang


@app.route('/translate', methods=['POST'])
def translate():
    form = request.form
    text = form['text']
    target = form['target']
    return _translate(text, target)


@celery.task
def _translate(text, target):
    translated_text = translator.translate(text, target)
    return translated_text.text


if __name__ == '__main__':
    app.run(debug=True)