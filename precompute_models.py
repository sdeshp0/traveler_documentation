import numpy as np
import pandas as pd
import pickle
import os
import re
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
from functools import lru_cache

# Load nltk resources
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_resources'))
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Load the datasets
FAQ_DF = pd.read_csv('data/travelerfaq.csv', index_col='Num')
FAQ_DF.index.name = None

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

# Apply preprocessing
FAQ_DF['Q&A'] = FAQ_DF['Question'] + ' ' + FAQ_DF['Answer']
FAQ_DF['processed'] = FAQ_DF['Q&A'].apply(preprocess_text)

# Precompute TFIDF Vectorizer
VECTORIZER = TfidfVectorizer(max_features=500, ngram_range=(1,2), stop_words='english')
TFIDF_MATRIX = VECTORIZER.fit_transform(FAQ_DF['processed'])

# Load a Pre-trained sentence embedding model
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute Embeddings
FAQ_DF['embedding'] = FAQ_DF['Q&A'].apply(lambda x: MODEL.encode(x))
FAQ_EMBEDDINGS = np.array(FAQ_DF["embedding"].tolist())

# Save models and processed data

FAQ_DF.to_csv('data/processed_faq.csv', index=False)
np.save('data/faq_embeddings.npy', np.array(FAQ_DF['embedding'].tolist()))
pickle.dump(VECTORIZER, open('data/tfidf_vectorizer.pkl', 'wb'))