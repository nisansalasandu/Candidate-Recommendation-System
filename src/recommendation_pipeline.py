import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pickle
import os


class CandidateRecommendationPipeline:
    def __init__(self, vectorizer_path=None):
        """
        Initialize the recommendation pipeline
        
        Args:
            vectorizer_path: Path to saved vectorizer (optional)
        """
        if vectorizer_path and os.path.exists(vectorizer_path):
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print(f"✓ Loaded vectorizer from {vectorizer_path}")
        else:
            # Initialize new vectorizer with optimized parameters
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.95
            )
            print("✓ Initialized new TF-IDF vectorizer")
    
    def clean_text(self, text):
        """
        Clean and preprocess text
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def calculate_similarity(self, job_texts, cv_texts):
        """
        Calculate cosine similarity between job descriptions and CVs
        
        Args:
            job_texts: List of job description texts
            cv_texts: List of CV texts
            
        Returns:
            Similarity matrix (jobs x CVs)
        """
        # Combine all texts for fitting
        all_texts = job_texts + cv_texts
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Split back into job and CV matrices
        n_jobs = len(job_texts)
        job_vectors = tfidf_matrix[:n_jobs]
        cv_vectors = tfidf_matrix[n_jobs:]
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(job_vectors, cv_vectors)
        
        return similarity_matrix
    
    def recommend_candidates(self, job_row, cvs_df, top_n=5):
        """
        Recommend top candidates for a single job
        
        Args:
            job_row: Single job row from DataFrame
            cvs_df: DataFrame of all CVs
            top_n: Number of top candidates to return
            
        Returns:
            DataFrame of top candidates with similarity scores
        """
        # Prepare texts
        job_text = job_row.get('cleaned_text', '')
        if not job_text:
            # Fallback to combining all job fields
            job_text = f"{job_row.get('required_skills', '')} {job_row.get('experience_required', '')} {job_row.get('education_required', '')} {job_row.get('job_description', '')}"
            job_text = self.clean_text(job_text)
        
        cv_texts = []
        for _, cv in cvs_df.iterrows():
            cv_text = cv.get('cleaned_text', '')
            if not cv_text:
                # Fallback to combining all CV fields
                cv_text = f"{cv.get('skills', '')} {cv.get('experience', '')} {cv.get('education', '')} {cv.get('cv_text', '')}"
                cv_text = self.clean_text(cv_text)
            cv_texts.append(cv_text)
        
        # Calculate similarities
        similarity_matrix = self.calculate_similarity([job_text], cv_texts)
        similarities = similarity_matrix[0]
        
        # Get top candidates
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        # Create results DataFrame
        results = []
        for idx in top_indices:
            cv_row = cvs_df.iloc[idx]
            results.append({
                'job_id': job_row['job_id'],
                'job_title': job_row['title'],
                'candidate_id': cv_row['candidate_id'],
                'candidate_name': cv_row['name'],
                'similarity_score': float(similarities[idx])
            })
        
        return pd.DataFrame(results)
    
    def batch_recommend(self, jobs_df, cvs_df, top_n=5):
        """
        Generate recommendations for all jobs
        
        Args:
            jobs_df: DataFrame of all jobs
            cvs_df: DataFrame of all CVs
            top_n: Number of top candidates per job
            
        Returns:
            DataFrame of all recommendations
        """
        all_recommendations = []
        
        for _, job_row in jobs_df.iterrows():
            job_recommendations = self.recommend_candidates(job_row, cvs_df, top_n)
            all_recommendations.append(job_recommendations)
        
        # Combine all recommendations
        if all_recommendations:
            return pd.concat(all_recommendations, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def save_vectorizer(self, path):
        """
        Save the trained vectorizer
        
        Args:
            path: Path to save the vectorizer
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print(f"✓ Saved vectorizer to {path}")
    
    def get_top_keywords(self, text, n=10):
        """
        Extract top keywords from text using TF-IDF
        
        Args:
            text: Input text
            n: Number of top keywords to return
            
        Returns:
            List of top keywords
        """
        # Transform text
        tfidf_vector = self.vectorizer.transform([self.clean_text(text)])
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top features
        top_indices = tfidf_vector.toarray()[0].argsort()[-n:][::-1]
        top_keywords = [feature_names[i] for i in top_indices if tfidf_vector.toarray()[0][i] > 0]
        
        return top_keywords


# Example usage
if __name__ == "__main__":
    # Example data
    jobs_data = {
        'job_id': ['J1', 'J2'],
        'title': ['Python Developer', 'Data Scientist'],
        'required_skills': ['Python Django Flask', 'Python Machine Learning'],
        'experience_required': ['3 years', '5 years'],
        'education_required': ['Bachelor', 'Master'],
        'job_description': ['Develop web applications', 'Build ML models']
    }
    
    cvs_data = {
        'candidate_id': ['C1', 'C2', 'C3'],
        'name': ['Alice', 'Bob', 'Charlie'],
        'skills': ['Python Django', 'Python ML TensorFlow', 'Java Spring'],
        'experience': ['4 years web dev', '6 years data science', '2 years backend'],
        'education': ['Bachelor CS', 'Master AI', 'Bachelor IT'],
        'cv_text': ['Full stack developer', 'ML engineer', 'Backend developer']
    }
    
    jobs_df = pd.DataFrame(jobs_data)
    cvs_df = pd.DataFrame(cvs_data)
    
    # Initialize pipeline
    pipeline = CandidateRecommendationPipeline()
    
    # Clean texts
    for df in [jobs_df, cvs_df]:
        df['cleaned_text'] = df.apply(
            lambda row: pipeline.clean_text(' '.join([str(v) for v in row.values])),
            axis=1
        )
    
    # Get recommendations
    recommendations = pipeline.batch_recommend(jobs_df, cvs_df, top_n=2)
    print("\nRecommendations:")
    print(recommendations)