# Candidate Recommendation System 🎯

**AI-Powered Talent Matching Using TF-IDF Vectorization & Cosine Similarity**

A complete full-stack web application that automatically matches candidates to job roles based on skills, experience, education, and CV content similarity.

---

## 🌟 Features

### Core Functionality
- **Vector-Based Matching**: Converts CVs and job descriptions into TF-IDF vectors for semantic comparison
- **Cosine Similarity Scoring**: Ranks candidates from best to least match (0-100% match score)
- **Multiple Input Methods**:
  - 📝 Manual text entry for quick testing
  - 📁 CSV file uploads for batch processing
  - 📊 JSON batch processing for API integration
- **Real-Time Processing**: Instant recommendations using pre-trained models
- **Export Results**: Download recommendations as CSV

### Technical Features
- Pre-trained TF-IDF vectorizer for consistent text representation
- NLTK-based text preprocessing (stopword removal, lemmatization)
- RESTful API for easy integration
- Modern, responsive web interface
- Comprehensive error handling and validation

---

## 📁 Project Structure

```
Candidate-Recommendation-System/
│
├── app.py                          # Flask backend server
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── data/                           # Original datasets
│   ├── cvs_100.csv                 # Sample candidate CVs
│   └── jobs_10.csv                 # Sample job descriptions
│
├── models/                         # Trained models (pickle files)
│   ├── vectorizer.pkl              # TF-IDF vectorizer
│   ├── cv_vectors.pkl              # Pre-computed CV vectors
│   └── job_vectors.pkl             # Pre-computed job vectors
│
├── src/                            # Source code modules
│   ├── preprocessing.py            # Text cleaning & preprocessing
│   ├── vectorization.py            # TF-IDF vectorization
│   ├── similarity.py               # Similarity computation
│   └── recommendation_pipeline.py  # Main pipeline for real-time recommendations
│
├── results/                        # Output files
│   ├── cvs_cleaned.csv            # Preprocessed CVs
│   ├── jobs_cleaned.csv           # Preprocessed jobs
│   └── top_candidates.csv         # Recommendation results
│
├── templates/                      # Frontend HTML
│   └── index.html                 # Main web interface
│
├── static/                         # Frontend assets
│   ├── script.js                  # JavaScript functionality
│   └── style.css                  # CSS styling
│
└── uploads/                        # Temporary file uploads
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install flask pandas scikit-learn nltk scipy
```

### Step 2: Download NLTK Data

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### Step 3: Train Models (First-Time Setup)

If you don't have pre-trained models in the `models/` folder:

```bash
# 1. Run preprocessing
cd src
python preprocessing.py

# 2. Train vectorizer and create vectors
python vectorization.py

# 3. (Optional) Test recommendations with sample data
python similarity.py
```

This will create:
- `models/vectorizer.pkl` - TF-IDF vectorizer
- `models/cv_vectors.pkl` - CV vectors
- `models/job_vectors.pkl` - Job vectors

### Step 4: Start the Server

```bash
python app.py
```

The server will start at: **http://localhost:5000**

---

## 🎯 How to Use

### Method 1: Manual Input (Quick Testing)

1. Navigate to **Manual Input** tab
2. Fill in the job description:
   - Required Skills
   - Experience Required
   - Education Required
   - Full Job Description
3. Add candidates using the "Add Candidate" button
4. Fill in candidate details (skills, experience, education, CV text)
5. Set the number of top candidates to recommend
6. Click **"Get Recommendations"**

### Method 2: File Upload (Batch Processing)

1. Navigate to **File Upload** tab
2. Prepare two CSV files:

**Candidates CSV** (columns):
- `candidate_id` (required)
- `skills`
- `experience`
- `education`
- `cv_text`

**Jobs CSV** (columns):
- `job_id` (required)
- `required_skills`
- `experience_required`
- `education_required`
- `job_description`

3. Upload both files
4. Set top N candidates per job
5. Click **"Upload & Process"**

### Method 3: Batch JSON (API Integration)

1. Navigate to **Batch Process** tab
2. Enter jobs in JSON array format:
```json
[
  {
    "job_id": "J001",
    "required_skills": "Python, Machine Learning",
    "experience_required": "3+ years",
    "education_required": "BS Computer Science",
    "job_description": "Looking for a Data Scientist..."
  }
]
```

3. Enter candidates in JSON array format:
```json
[
  {
    "candidate_id": "C001",
    "skills": "Python, TensorFlow, Keras",
    "experience": "4 years as ML Engineer",
    "education": "MS Computer Science",
    "cv_text": "Experienced in building ML models..."
  }
]
```

4. Click **"Process Batch"**

---

## 🔧 API Endpoints

### Health Check
```
GET /api/health
```
Returns system status

### Single Job Recommendation
```
POST /api/recommend
Content-Type: application/json

{
  "job": {
    "required_skills": "...",
    "experience_required": "...",
    "education_required": "...",
    "job_description": "..."
  },
  "candidates": [
    {
      "candidate_id": "C001",
      "skills": "...",
      "experience": "...",
      "education": "...",
      "cv_text": "..."
    }
  ],
  "top_n": 5
}
```

### File Upload Recommendation
```
POST /api/recommend/file
Content-Type: multipart/form-data

Form Data:
- cvs_file: CSV file
- jobs_file: CSV file
- top_n: integer (optional)
```

### Batch Recommendation
```
POST /api/batch/recommend
Content-Type: application/json

{
  "jobs": [...],
  "candidates": [...],
  "top_n": 5
}
```

### Process Single CV
```
POST /api/process/cv
Content-Type: application/json

{
  "skills": "...",
  "experience": "...",
  "education": "...",
  "cv_text": "..."
}
```

### Process Single Job
```
POST /api/process/job
Content-Type: application/json

{
  "required_skills": "...",
  "experience_required": "...",
  "education_required": "...",
  "job_description": "..."
}
```

---

## 🧠 How It Works

### 1. **Text Preprocessing**
```python
# Steps performed on all text:
1. Convert to lowercase
2. Remove punctuation and numbers
3. Tokenize into words
4. Remove stopwords (common words like "the", "is", "and")
5. Lemmatize (convert words to base form: "running" → "run")
```

### 2. **Vectorization (TF-IDF)**
```
TF-IDF (Term Frequency-Inverse Document Frequency):
- Converts text to numerical vectors
- Weighs words by importance (rare words get higher scores)
- Max 5000 features for efficiency
- Same vectorizer used for both CVs and jobs (consistency)
```

### 3. **Similarity Computation**
```
Cosine Similarity:
- Measures angle between two vectors
- Range: 0 (no match) to 1 (perfect match)
- Formula: cos(θ) = (A · B) / (||A|| × ||B||)
```

### 4. **Ranking & Recommendation**
```
1. Compute similarity scores for all CV-Job pairs
2. Sort candidates by similarity score (descending)
3. Select top N candidates
4. Return with rank, score, and match percentage
```

---

## 📊 Sample Output

```json
{
  "success": true,
  "total_candidates": 10,
  "recommendations": [
    {
      "candidate_id": "C003",
      "similarity_score": 0.8756,
      "rank": 1,
      "match_percentage": 87.56
    },
    {
      "candidate_id": "C007",
      "similarity_score": 0.7823,
      "rank": 2,
      "match_percentage": 78.23
    },
    ...
  ]
}
```

---

## 📈 Results & Evaluation

### Metrics
- **Cosine Similarity Score**: 0-1 (higher = better match)
- **Match Percentage**: 0-100% (normalized score)
- **Rank**: 1, 2, 3... (1 = best match)

### Visual Features
- 🥇 Gold badge for #1 rank
- 🥈 Silver badge for #2 rank
- 🥉 Bronze badge for #3 rank
- Color-coded progress bars:
  - 🟢 Green (70%+): Excellent match
  - 🟡 Yellow (50-70%): Good match
  - 🔴 Red (<50%): Weak match

---

## 🎨 Frontend Features

- **Modern UI**: Gradient backgrounds, smooth animations
- **Tabbed Navigation**: Switch between input methods easily
- **Real-Time Feedback**: Loading spinners, error messages
- **Responsive Design**: Works on desktop, tablet, mobile
- **Export Functionality**: Download results as CSV
- **Statistics Dashboard**: Total jobs, candidates, matches

---

## 🔒 Security & Best Practices

- File size limit: 16MB
- Input validation on all endpoints
- Error handling with descriptive messages
- CORS-ready for API integration
- No sensitive data stored (stateless)

---

## 🚧 Known Limitations

1. **Model Version Warning**: If you see scikit-learn version warnings, consider retraining the vectorizer with your current scikit-learn version
2. **Memory Usage**: Processing large CSV files (1000+ rows) may require additional memory
3. **Development Server**: Current setup uses Flask's development server. For production, use Gunicorn or uWSGI

---

## 🔄 Retraining the Model

If you update dependencies or want to retrain:

```bash
cd src

# Step 1: Preprocess new data
python preprocessing.py

# Step 2: Retrain vectorizer
python vectorization.py

# Step 3: Test
python similarity.py

# Step 4: Restart server
cd ..
python app.py
```

---

## 🛠️ Troubleshooting

### Issue: "Vectorizer not found"
**Solution**: Run training scripts in `src/` folder first

### Issue: NLTK data errors
**Solution**: 
```bash
python -c "import nltk; nltk.download('all')"
```

### Issue: Version warnings
**Solution**: Retrain models or ignore (usually harmless)

### Issue: Port 5000 already in use
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

---

## 📝 Project Requirements Met

✅ **Vector Representations**: TF-IDF vectorization for CVs and jobs  
✅ **Preprocessing**: Cleaning, tokenization, stopword removal, lemmatization  
✅ **Similarity Computation**: Cosine similarity implementation  
✅ **Top N Recommendations**: Ranked candidate list for each job  
✅ **Evaluation**: Similarity scores, match percentages, visual ranking  
✅ **Full-Stack Application**: Backend API + Frontend UI  
✅ **Documentation**: Complete README with usage instructions  
✅ **Code Organization**: Modular structure with separate folders  

---

## 👥 Contributors

Group Project - AI/ML Course

---

## 📄 License

This project is for educational purposes.

---

## 🎓 Academic Context

This system was developed as part of a group project to build a Candidate Recommendation Engine. The implementation covers:

- **Machine Learning**: TF-IDF vectorization, cosine similarity
- **Natural Language Processing**: Text preprocessing, lemmatization
- **Software Engineering**: Modular design, API development
- **Full-Stack Development**: Flask backend, responsive frontend
- **Data Science**: CSV processing, batch analysis, evaluation metrics

---

## 🚀 Future Enhancements

- [ ] Add BERT/Transformer-based embeddings
- [ ] Implement user authentication
- [ ] Add database support (PostgreSQL/MongoDB)
- [ ] Create admin dashboard
- [ ] Add email notifications
- [ ] Implement caching for faster responses
- [ ] Add more similarity metrics (Euclidean, Jaccard)
- [ ] Create Docker container for easy deployment
- [ ] Add unit tests and integration tests

---

## 📞 Support

For issues or questions, please check:
1. This README
2. Code comments in source files
3. Error messages in the browser console or terminal

---

**🎉 Happy Recruiting! 🎉**
