import numpy as np
import pandas as pd
import pickle
import os
import re
import nltk
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

# Load nltk resources
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_resources'))
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Preprocess text
def preprocess_text(text):
    """Clean and normalize text for better matching."""
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    words = text.split()
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)


def split_into_sentences(text):
    """Splits text into sentences using basic punctuation rules."""
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    return sentence_endings.split(text.strip())


def truncate_to_full_sentences(text, max_chars=3000):
    """Truncates text to nearest full sentence without exceeding character limit."""
    sentences = split_into_sentences(text)
    truncated = ''
    for sentence in sentences:
        if len(truncated) + len(sentence) > max_chars:
            break
        truncated += sentence.strip() + ' '
    return truncated.strip()


def truncate_summary(summary_text, max_chars=400):
    """Truncate the summary to full sentences within a character limit."""
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(summary_text.strip())

    truncated = ''
    for sentence in sentences:
        if len(truncated) + len(sentence) > max_chars:
            break
        truncated += sentence.strip() + ' '
    return truncated.strip()


def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def preprocess_data():
    # Load the datasets
    FAQ_DF = pd.read_csv('data/travelerfaq.csv', index_col='Num')
    # Apply preprocessing
    FAQ_DF['Q&A'] = FAQ_DF['Question'] + ' ' + FAQ_DF['Answer']
    FAQ_DF['processed'] = FAQ_DF['Q&A'].apply(preprocess_text)

    # Precompute TFIDF Vectorizer
    VECTORIZER = TfidfVectorizer(max_features=500, ngram_range=(1,2), stop_words='english')
    TFIDF_MATRIX = VECTORIZER.fit_transform(FAQ_DF['processed'])

    MODEL = SentenceTransformer('all-MiniLM-L6-v2')

    # Precompute Embeddings
    FAQ_DF['embedding'] = FAQ_DF['Q&A'].apply(lambda x: MODEL.encode(x))

    # Save models and processed data

    FAQ_DF.to_csv('data/processed_faq.csv')
    np.save('data/faq_embeddings.npy', np.array(FAQ_DF['embedding'].tolist()))
    pickle.dump(VECTORIZER, open('data/tfidf_vectorizer.pkl', 'wb'))
    pickle.dump(TFIDF_MATRIX, open('data/tfidf_matrix.pkl', 'wb'))


if __name__ == '__main__':
    preprocess_data()