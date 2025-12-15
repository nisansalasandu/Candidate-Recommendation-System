# vectorization.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle  # to save vectorizer for future use

# ----------------------------
# Load cleaned datasets
# ----------------------------
cvs = pd.read_csv("../results/cvs_cleaned.csv")
jobs = pd.read_csv("../results/jobs_cleaned.csv")

# ----------------------------
# TF-IDF Vectorization
# ----------------------------
vectorizer = TfidfVectorizer(max_features=5000)  # limit features to 5000 for efficiency

# Fit on CVs and transform CV text
cv_vectors = vectorizer.fit_transform(cvs['cleaned_text'])

# Transform Job Descriptions (use the same vectorizer)
job_vectors = vectorizer.transform(jobs['cleaned_text'])

# ----------------------------
# Save vectors for later use
# ----------------------------
with open("../models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

# Save CV vectors
with open("../models/cv_vectors.pkl", "wb") as f:
    pickle.dump(cv_vectors, f)

# Save Job vectors
with open("../models/job_vectors.pkl", "wb") as f:
    pickle.dump(job_vectors, f)

print("Vectorization completed. Vectors saved in /models/")


# End of vectorization.py