# recommendation.py
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# Load cleaned datasets
# ----------------------------
cvs = pd.read_csv("../results/cvs_cleaned.csv")
jobs = pd.read_csv("../results/jobs_cleaned.csv")

# ----------------------------
# Load vectors
# ----------------------------
with open("../models/cv_vectors.pkl", "rb") as f:
    cv_vectors = pickle.load(f)

with open("../models/job_vectors.pkl", "rb") as f:
    job_vectors = pickle.load(f)

# ----------------------------
# Compute Cosine Similarity
# ----------------------------
similarity_matrix = cosine_similarity(job_vectors, cv_vectors)
# similarity_matrix[i][j] = similarity of job i with candidate j

# ----------------------------
# Recommend Top N Candidates
# ----------------------------
top_n = 5  # choose top 5 candidates

recommendations = []

for job_idx, job in jobs.iterrows():
    # Get similarity scores for this job
    scores = similarity_matrix[job_idx]
    
    # Get indices of top N candidates
    top_indices = np.argsort(scores)[::-1][:top_n]
    
    for rank, idx in enumerate(top_indices, start=1):
        recommendations.append({
            "job_id": job['job_id'],
            #"job_title": job['job_title'],
            "candidate_id": cvs.iloc[idx]['candidate_id'],
            "similarity_score": round(scores[idx], 4),
            "rank": rank
        })

# ----------------------------
# Save recommendations
# ----------------------------
recommendations_df = pd.DataFrame(recommendations)
recommendations_df.to_csv("../results/top_candidates.csv", index=False)

print("Recommendation completed. Top candidates saved in /results/top_candidates.csv")

# End of recommendation.py