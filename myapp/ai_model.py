import PyPDF2
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle

class HealthcareAI:
    def __init__(self):
        self.knowledge_base = []
        self.vectorizer = TfidfVectorizer()
        self.vectors = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'trained_model')
        
        # Create model directory if it doesn't exist
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
    
    def save_model(self):
        """Save the trained model state"""
        model_file = os.path.join(self.model_path, 'healthcare_model.pkl')
        model_data = {
            'knowledge_base': self.knowledge_base,
            'vectorizer': self.vectorizer,
            'vectors': self.vectors
        }
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        """Load the trained model state"""
        model_file = os.path.join(self.model_path, 'healthcare_model.pkl')
        if os.path.exists(model_file):
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
                self.knowledge_base = model_data['knowledge_base']
                self.vectorizer = model_data['vectorizer']
                self.vectors = model_data['vectors']
            return True
        return False