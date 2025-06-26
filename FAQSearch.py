import numpy as np
import pandas as pd
import pickle
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from precompute_models import preprocess_text, truncate_to_full_sentences, truncate_summary
from collections import OrderedDict
from functools import lru_cache


class GlossarySearch:
    def __init__(self, query, faq_df, glossary_df):
        self.query = query
        self.faq_df = faq_df
        self.glossary_df = glossary_df
        self.queryTags = self.query_tags()
        self.questionNums = self.question_list()
        self.result = self.query_faq()

    def query_tags(self):
        return [t for t in self.glossary_df.index if self.query in t]

    def question_list(self):
        if len(self.queryTags) > 0:
            ql = self.glossary_df.loc[self.query.lower(), 'RelatedQuestions']
            ql = ql.strip("[]")
            ql = [int(i) for i in ql.split(", ")]
            return ql
        else:
            return None

    def query_faq(self):
        if self.questionNums:
            return self.faq_df.loc[self.questionNums,['Question', 'RelatedTags', 'Answer']]
        else:
            return None


class HybridSearch:
    def __init__(
        self,
        query,
        faq_df,
        faq_embeddings,
        tfidf_matrix,
        tfidf_vectorizer,
        summarizer,
        top_n=5,
        similarity_threshold=0.3,
        embedding_weight=0.6,
        cache_size=50,
    ):
        self.query = query
        self.faq_df = faq_df
        self.faq_embeddings = faq_embeddings
        self.tfidf_matrix = tfidf_matrix
        self.vectorizer = tfidf_vectorizer
        self.summarizer = summarizer
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold
        self.embedding_weight = embedding_weight
        self.cache_size = cache_size
        self.cache = OrderedDict()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.results = self.hybrid_search_faq()

    def update_cache(self, query, result):
        """Store query results and dynamically remove older entries."""
        if query in self.cache:
            self.cache.move_to_end(query)  # Maintain order for repeated queries
        else:
            self.cache[query] = result  # Add new entry
            if len(self.cache) > self.cache_size:  # Enforce cache limit
                self.cache.popitem(last=False)  # Remove oldest item

    def safe_summary(self, text, desired_max=200, desired_min=60):
        num_words = len(text.split())
        max_len = min(desired_max, int(num_words * 0.8))  # Adjust to 80% of input length
        max_len = max(max_len, desired_min+1)                 # Ensure max > min
        return self.summarizer(text,
                               max_length=max_len,
                               min_length=desired_min,
                               do_sample=False,
                               truncation=True
                               )[0]['summary_text']

    def hybrid_search_faq(self):
        """Retrieve top N most relevant FAQ entries using hybrid method."""
        if self.query in self.cache:
            return self.cache[self.query]  # Return cached result

        query_preprocessed = preprocess_text(self.query)

        # TF-IDF Search
        query_vec = self.vectorizer.transform([query_preprocessed])
        tfidf_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Embedding-Based Search
        query_embedding = self.model.encode(query_preprocessed)
        embedding_similarities = cosine_similarity([query_embedding], self.faq_embeddings).flatten()

        # Hybrid Score Fusion
        combined_scores = (tfidf_similarities * (1 - self.embedding_weight)) + (
                    embedding_similarities * self.embedding_weight)

        # Filter and sort results
        top_indices = combined_scores.argsort()[::-1]
        top_matches = [(i, combined_scores[i]) for i in top_indices if combined_scores[i] > self.similarity_threshold]

        # Get top-N results
        top_rows = self.faq_df.iloc[[i[0] for i in top_matches[:self.top_n]]][['Question', 'RelatedTags', 'Answer']]

        if not top_rows.empty:
            answers = top_rows["Answer"].tolist()
            concatenated_text = " ".join(answers)
            clean_text = truncate_to_full_sentences(concatenated_text)

            # Scale summary length based on how many answers are matched
            match_count = len(answers)
            max_len = min(300, 60 + 60 * match_count)  # Cap at 300 tokens
            min_len = min(100, 20 + 20 * match_count)

            summary = self.safe_summary(text=clean_text, desired_max=max_len, desired_min=min_len)
            summary = truncate_summary(summary)
        else:
            summary = 'No relevant entries were found for your query. Please try again with a different query.'

        results = {
            "summary": summary,
            "matches": top_rows
        }

        # Store result in cache
        self.update_cache(self.query, results)
        return results


_='''
Deprecated Classes
Embedding-Search and TFIDF Search have been combined into a Hybrid Search


class TFIDFsearch:
    def __init__(self, query, summarizer, top_n=5, similarity_threshold=0.25):
        """Initialize the FAQ search system with a query."""
        self.query = query
        self.summarizer = summarizer
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold

        # Perform search upon initialization with caching
        self.results = self.cached_search_faq(self.query, self.top_n, self.similarity_threshold)

    @lru_cache(maxsize=10)  # Cache up to 10 queries
    def cached_search_faq(self, query, top_n, similarity_threshold):
        """Retrieve top N most relevant FAQ entries based on query using caching."""
        query_vec = VECTORIZER.transform([preprocess_text(query)])
        similarities = cosine_similarity(query_vec, TFIDF_MATRIX).flatten()

        # Filter and sort by similarity score
        top_indices = similarities.argsort()[::-1]
        top_matches = [(i, similarities[i]) for i in top_indices if similarities[i] > similarity_threshold]

        # Get top-N results
        top_rows = FAQ_DF.iloc[[i[0] for i in top_matches[:top_n]]][['Question', 'RelatedTags', 'Answer']]

        if not top_rows.empty:
            # Generate summary from concatenated answers
            concatenated_answers = " ".join(top_rows["Answer"].tolist())[:1024]  # Limit for model input
            summarizer = self.summarizer
            summary = summarizer(concatenated_answers, max_length=75, min_length=25, do_sample=False)[0]["summary_text"]
        else:
            summary = 'No relevant entries were found for your query. Please try again with a different query.'

        results = {
            "summary": summary,
            "matches": top_rows
        }

        return results


class EmbeddingSearch:
    def __init__(self, query, summarizer, top_n=5, similarity_threshold=0.5, cache_size=10):
        """Initialize FAQ search using embedding-based similarity."""
        self.query = query
        self.summarizer = summarizer
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
        top_rows = FAQ_DF.iloc[[i[0] for i in top_matches[:self.top_n]]][['Question', 'RelatedTags', 'Answer']]

        if not top_rows.empty:

            # Generate summary from concatenated answers
            concatenated_answers = " ".join(top_rows["Answer"].tolist())[:1024]  # Limit for model input
            summarizer = self.summarizer
            summary = summarizer(concatenated_answers, max_length=75, min_length=25, do_sample=False)[0]["summary_text"]

        else:
            summary = 'No relevant entries were found for your query. Please try again with a different query.'

        results = {
            "summary": summary,
            "matches": top_rows
        }

        # Store result in cache
        self.update_cache(self.query, results)
        return results

'''