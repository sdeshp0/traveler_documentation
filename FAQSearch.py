import numpy as np
import pandas as pd
import re
import os
import nltk
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
from functools import lru_cache

torch.classes.__path__ = [] # add this line to manually set empty path and avoid warning in streamlit
# Load nltk resources

nltk.data.path.append(os.path.join(os.getcwd(), "nltk_resources"))
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Load the datasets
FAQ_DF = pd.read_csv('data/travelerfaq.csv', index_col='Num')
GLOSSARY_DF = pd.read_csv('data/glossary.csv')

GLOSSARY_DF.reset_index(inplace=True)
glossary_tags = [t.lower() for t in GLOSSARY_DF['Tag']]
GLOSSARY_DF.index = glossary_tags
GLOSSARY_DF.drop('Tag', inplace=True, axis=1)
GLOSSARY_DF.index.name='Tag'
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

# Fit TF-IDF model once globally
VECTORIZER = TfidfVectorizer(max_features=500, ngram_range=(1,2), stop_words='english')
TFIDF_MATRIX = VECTORIZER.fit_transform(FAQ_DF['processed'])

# Load a Pre-trained sentence embedding model
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Compute Embeddings once globally
FAQ_DF['embedding'] = FAQ_DF['Q&A'].apply(lambda x: MODEL.encode(x))
FAQ_EMBEDDINGS = np.array(FAQ_DF["embedding"].tolist())

class GlossarySearch:
    def __init__(self, query):
        self.query = query
        self.queryTags = self.query_tags()
        self.questionNums = self.question_list()
        self.result = self.query_faq()

    def query_tags(self):
        return [t for t in GLOSSARY_DF.index if self.query in t]

    def question_list(self):
        if len(self.queryTags) > 0:
            ql = GLOSSARY_DF.loc[self.query.lower(), 'RelatedQuestions']
            ql = ql.strip("[]")
            ql = [int(i) for i in ql.split(", ")]
            return ql
        else:
            return None

    def query_faq(self):
        if self.questionNums:
            return FAQ_DF.loc[self.questionNums,['Question', 'RelatedTags', 'Answer']]
        else:
            return None


class TFIDFsearch:
    def __init__(self, query, top_n=10, similarity_threshold=0.25):
        """Initialize the FAQ search system with a query."""
        self.query = query
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold

        # Perform search upon initialization with caching
        self.results = self.cached_search_faq(self.query, self.top_n, self.similarity_threshold)

    @lru_cache(maxsize=25)  # Cache up to 25 queries
    def cached_search_faq(self, query, top_n, similarity_threshold):
        """Retrieve top N most relevant FAQ entries based on query using caching."""
        query_vec = VECTORIZER.transform([preprocess_text(query)])
        similarities = cosine_similarity(query_vec, TFIDF_MATRIX).flatten()

        # Filter and sort by similarity score
        top_indices = similarities.argsort()[::-1]
        top_matches = [(i, similarities[i]) for i in top_indices if similarities[i] > similarity_threshold]

        # Get top-N results
        results = FAQ_DF.iloc[[i[0] for i in top_matches[:top_n]]][['Question', 'RelatedTags', 'Answer']]
        return results


class EmbeddingSearch:
    def __init__(self, query, top_n=10, similarity_threshold=0.5, cache_size=25):
        """Initialize FAQ search using embedding-based similarity."""
        self.query = query
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold
        self.cache_size = cache_size
        self.cache = OrderedDict()  # Initialize cache storage

        # Perform search upon initialization
        self.results = self.search_faq()

    def update_cache(self, query, result):
        """Store query results and dynamically remove older entries."""
        if query in self.cache:
            self.cache.move_to_end(query)  # Maintain order for repeated queries
        else:
            self.cache[query] = result  # Add new entry
            if len(self.cache) > self.cache_size:  # Enforce cache limit
                self.cache.popitem(last=False)  # Remove oldest item

    def search_faq(self):
        """Retrieve top N most relevant FAQ entries based on embedding similarity."""
        if self.query in self.cache:
            return self.cache[self.query]  # Return cached result

        query_embedding = MODEL.encode(preprocess_text(self.query))
        similarities = cosine_similarity([query_embedding], FAQ_EMBEDDINGS).flatten()

        # Filter and sort by similarity score
        top_indices = similarities.argsort()[::-1]
        top_matches = [(i, similarities[i]) for i in top_indices if similarities[i] > self.similarity_threshold]

        # Get top-N results
        results = FAQ_DF.iloc[[i[0] for i in top_matches[:self.top_n]]][['Question', 'RelatedTags', 'Answer']]
        results = results

        # Store result in cache
        self.update_cache(self.query, results)
        return results


class HybridSearch:
    def __init__(self, query, top_n=5, similarity_threshold=0.3, embedding_weight=0.6, cache_size=25):
        """Initialize FAQ hybrid search with query."""
        self.query = query
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold
        self.embedding_weight = embedding_weight  # Adjust influence of embeddings
        self.cache_size = cache_size
        self.cache = OrderedDict()  # Initialize cache storage

        # Perform search upon initialization
        self.results = self.hybrid_search_faq()

    def update_cache(self, query, result):
        """Store query results and dynamically remove older entries."""
        if query in self.cache:
            self.cache.move_to_end(query)  # Maintain order for repeated queries
        else:
            self.cache[query] = result  # Add new entry
            if len(self.cache) > self.cache_size:  # Enforce cache limit
                self.cache.popitem(last=False)  # Remove oldest item

    def hybrid_search_faq(self):
        """Retrieve top N most relevant FAQ entries using hybrid method."""
        if self.query in self.cache:
            return self.cache[self.query]  # Return cached result

        query_preprocessed = preprocess_text(self.query)

        # TF-IDF Search
        query_vec = VECTORIZER.transform([query_preprocessed])
        tfidf_similarities = cosine_similarity(query_vec, TFIDF_MATRIX).flatten()

        # Embedding-Based Search
        query_embedding = MODEL.encode(query_preprocessed)
        embedding_similarities = cosine_similarity([query_embedding], FAQ_EMBEDDINGS).flatten()

        # Hybrid Score Fusion
        combined_scores = (tfidf_similarities * (1 - self.embedding_weight)) + (
                    embedding_similarities * self.embedding_weight)

        # Filter and sort results
        top_indices = combined_scores.argsort()[::-1]
        top_matches = [(i, combined_scores[i]) for i in top_indices if combined_scores[i] > self.similarity_threshold]

        # Get top-N results
        results = FAQ_DF.iloc[[i[0] for i in top_matches[:self.top_n]]][['Question', 'RelatedTags', 'Answer']]
        results = results

        # Store result in cache
        self.update_cache(self.query, results)
        return results
