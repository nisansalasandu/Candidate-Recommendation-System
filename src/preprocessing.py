# preprocessing.py

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ----------------------------
# Function to clean text
# ----------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    # Lowercase
    text = text.lower()
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

# ----------------------------
# Load datasets
# ----------------------------
cvs = pd.read_csv("../data/cvs_100.csv")
jobs = pd.read_csv("../data/jobs_10.csv")

# ----------------------------
# Combine text fields for CVs
# ----------------------------
cvs['combined_text'] = cvs['skills'].fillna('') + ' ' + \
                       cvs['experience'].fillna('') + ' ' + \
                       cvs['education'].fillna('') + ' ' + \
                       cvs['cv_text'].fillna('')

# Apply cleaning
cvs['cleaned_text'] = cvs['combined_text'].apply(clean_text)

# ----------------------------
# Combine text fields for Job Descriptions
# ----------------------------
jobs['combined_text'] = jobs['required_skills'].fillna('') + ' ' + \
                        jobs['experience_required'].fillna('') + ' ' + \
                        jobs['education_required'].fillna('') + ' ' + \
                        jobs['job_description'].fillna('')

# Apply cleaning
jobs['cleaned_text'] = jobs['combined_text'].apply(clean_text)

# ----------------------------
# Save cleaned datasets
# ----------------------------
cvs[['candidate_id','cleaned_text']].to_csv("../results/cvs_cleaned.csv", index=False)
jobs[['job_id','cleaned_text']].to_csv("../results/jobs_cleaned.csv", index=False)

print("Preprocessing completed. Cleaned files saved in /results/")

# End of preprocessing.py