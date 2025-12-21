"""
recommendation_pipeline.py
Complete pipeline for candidate recommendation using trained models
"""

import pandas as pd
import numpy as np
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data (silent mode)
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('wordnet', quiet=True)

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


class CandidateRecommendationPipeline:
    """
    Complete pipeline for candidate recommendation system
    Loads trained models and provides real-time recommendations
    """
    
    def __init__(self, vectorizer_path='models/vectorizer.pkl'):
        """Initialize the pipeline by loading the trained vectorizer"""
        self.vectorizer = None
        self.vectorizer_path = vectorizer_path
        self.load_vectorizer()
    
    def load_vectorizer(self):
        """Load the trained TF-IDF vectorizer from pickle file"""
        try:
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print(f"✓ Vectorizer loaded successfully from {self.vectorizer_path}")
        except FileNotFoundError:
            raise Exception(f"Vectorizer not found at {self.vectorizer_path}. Please train the model first.")
        except Exception as e:
            raise Exception(f"Error loading vectorizer: {str(e)}")
    
    def clean_text(self, text):
        """
        Clean and preprocess text using the same method as training
        
        Steps:
        1. Convert to lowercase
        2. Remove punctuation and numbers
        3. Tokenize
        4. Remove stopwords
        5. Lemmatize
        """
        if pd.isna(text) or text == "":
            return ""
        
        # Lowercase
        text = str(text).lower()
        
        # Remove punctuation and numbers
        text = re.sub(r'[^a-z\s]', '', text)
        
        # Tokenize
        words = nltk.word_tokenize(text)
        
        # Remove stopwords
        words = [w for w in words if w not in stop_words]
        
        # Lemmatize
        words = [lemmatizer.lemmatize(w) for w in words]
        
        # Join back into string
        return ' '.join(words)
    
    def process_cv(self, skills='', experience='', education='', cv_text=''):
        """
        Process a single CV and return cleaned text
        
        Args:
            skills: Skills text
            experience: Experience text
            education: Education text
            cv_text: Full CV text
        
        Returns:
            Cleaned and processed text
        """
        # Combine all fields
        combined = f"{skills} {experience} {education} {cv_text}"
        
        # Clean the text
        cleaned = self.clean_text(combined)
        
        return cleaned
    
    def process_job(self, required_skills='', experience_required='', 
                   education_required='', job_description=''):
        """
        Process a single job description and return cleaned text
        
        Args:
            required_skills: Required skills
            experience_required: Experience requirements
            education_required: Education requirements
            job_description: Full job description
        
        Returns:
            Cleaned and processed text
        """
        # Combine all fields
        combined = f"{required_skills} {experience_required} {education_required} {job_description}"
        
        # Clean the text
        cleaned = self.clean_text(combined)
        
        return cleaned
    
    def vectorize_text(self, text):
        """
        Convert cleaned text to TF-IDF vector using trained vectorizer
        
        Args:
            text: Cleaned text string
        
        Returns:
            TF-IDF vector (sparse matrix)
        """
        if self.vectorizer is None:
            raise Exception("Vectorizer not loaded. Call load_vectorizer() first.")
        
        return self.vectorizer.transform([text])
    
    def compute_similarity(self, cv_vectors, job_vectors):
        """
        Compute cosine similarity between CVs and job descriptions
        
        Args:
            cv_vectors: CV vectors (sparse matrix or array)
            job_vectors: Job vectors (sparse matrix or array)
        
        Returns:
            Similarity matrix (numpy array)
        """
        return cosine_similarity(job_vectors, cv_vectors)
    
    def recommend_candidates(self, job_data, cv_data_list, top_n=5):
        """
        Recommend top N candidates for a given job
        
        Args:
            job_data: Dictionary with job fields
                     {required_skills, experience_required, education_required, job_description}
            cv_data_list: List of dictionaries with CV fields
                         [{candidate_id, skills, experience, education, cv_text}, ...]
            top_n: Number of top candidates to recommend
        
        Returns:
            List of dictionaries with recommendations
            [{candidate_id, similarity_score, rank}, ...]
        """
        # Process job description
        job_cleaned = self.process_job(
            required_skills=job_data.get('required_skills', ''),
            experience_required=job_data.get('experience_required', ''),
            education_required=job_data.get('education_required', ''),
            job_description=job_data.get('job_description', '')
        )
        
        # Vectorize job
        job_vector = self.vectorize_text(job_cleaned)
        
        # Process and vectorize all CVs
        cv_vectors_list = []
        candidate_ids = []
        
        for cv_data in cv_data_list:
            cv_cleaned = self.process_cv(
                skills=cv_data.get('skills', ''),
                experience=cv_data.get('experience', ''),
                education=cv_data.get('education', ''),
                cv_text=cv_data.get('cv_text', '')
            )
            
            cv_vector = self.vectorize_text(cv_cleaned)
            cv_vectors_list.append(cv_vector)
            candidate_ids.append(cv_data.get('candidate_id', f"CV_{len(candidate_ids)+1}"))
        
        # Stack CV vectors
        from scipy.sparse import vstack
        cv_vectors = vstack(cv_vectors_list)
        
        # Compute similarity
        similarity_scores = self.compute_similarity(cv_vectors, job_vector)
        scores = similarity_scores[0]  # Get scores for the single job
        
        # Get top N candidates
        top_indices = np.argsort(scores)[::-1][:top_n]
        
        # Build recommendations
        recommendations = []
        for rank, idx in enumerate(top_indices, start=1):
            recommendations.append({
                'candidate_id': candidate_ids[idx],
                'similarity_score': float(round(scores[idx], 4)),
                'rank': rank,
                'match_percentage': float(round(scores[idx] * 100, 2))
            })
        
        return recommendations
    
    def batch_recommend(self, jobs_df, cvs_df, top_n=5):
        """
        Process batch recommendations from DataFrames
        
        Args:
            jobs_df: DataFrame with job descriptions
            cvs_df: DataFrame with candidate CVs
            top_n: Number of top candidates per job
        
        Returns:
            DataFrame with all recommendations
        """
        all_recommendations = []
        
        # Process all CVs
        cv_vectors_list = []
        for _, cv in cvs_df.iterrows():
            cv_cleaned = self.process_cv(
                skills=cv.get('skills', ''),
                experience=cv.get('experience', ''),
                education=cv.get('education', ''),
                cv_text=cv.get('cv_text', '')
            )
            cv_vector = self.vectorize_text(cv_cleaned)
            cv_vectors_list.append(cv_vector)
        
        # Stack CV vectors
        from scipy.sparse import vstack
        cv_vectors = vstack(cv_vectors_list)
        
        # Process each job
        for _, job in jobs_df.iterrows():
            job_cleaned = self.process_job(
                required_skills=job.get('required_skills', ''),
                experience_required=job.get('experience_required', ''),
                education_required=job.get('education_required', ''),
                job_description=job.get('job_description', '')
            )
            
            job_vector = self.vectorize_text(job_cleaned)
            
            # Compute similarity
            similarity_scores = self.compute_similarity(cv_vectors, job_vector)
            scores = similarity_scores[0]
            
            # Get top N candidates
            top_indices = np.argsort(scores)[::-1][:top_n]
            
            # Build recommendations for this job
            for rank, idx in enumerate(top_indices, start=1):
                all_recommendations.append({
                    'job_id': job['job_id'],
                    'candidate_id': cvs_df.iloc[idx]['candidate_id'],
                    'similarity_score': round(scores[idx], 4),
                    'rank': rank,
                    'match_percentage': round(scores[idx] * 100, 2)
                })
        
        return pd.DataFrame(all_recommendations)


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = CandidateRecommendationPipeline()
    
    # Example: Single job with multiple candidates
    job = {
        'required_skills': 'Python, Machine Learning, Data Science',
        'experience_required': '3+ years in software development',
        'education_required': 'Bachelor in Computer Science',
        'job_description': 'Looking for a data scientist with strong Python skills'
    }
    
    candidates = [
        {
            'candidate_id': 'C001',
            'skills': 'Python, TensorFlow, Machine Learning',
            'experience': '4 years as Data Scientist',
            'education': 'MS in Computer Science',
            'cv_text': 'Experienced in building ML models and data pipelines'
        },
        {
            'candidate_id': 'C002',
            'skills': 'Java, Spring Boot, Microservices',
            'experience': '2 years as Backend Developer',
            'education': 'BS in Software Engineering',
            'cv_text': 'Backend developer with Java expertise'
        }
    ]
    
    # Get recommendations
    recommendations = pipeline.recommend_candidates(job, candidates, top_n=2)
    
    print("\n=== Candidate Recommendations ===")
    for rec in recommendations:
        print(f"Rank {rec['rank']}: {rec['candidate_id']} - "
              f"Score: {rec['similarity_score']} ({rec['match_percentage']}%)")
