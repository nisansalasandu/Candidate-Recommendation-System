# System Architecture - Candidate Recommendation System

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Browser - index.html)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Manual Input │  │ File Upload  │  │ Batch JSON   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                            │
│                         (app.py)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API ENDPOINTS                          │  │
│  │  • /api/recommend                                        │  │
│  │  • /api/recommend/file                                   │  │
│  │  • /api/batch/recommend                                  │  │
│  │  • /api/process/cv                                       │  │
│  │  • /api/process/job                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              RECOMMENDATION PIPELINE                             │
│        (src/recommendation_pipeline.py)                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Text         │  │ Vectorization│  │  Similarity  │         │
│  │ Preprocessing│─▶│   (TF-IDF)   │─▶│  (Cosine)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Cleaning   │  │Load Trained  │  │   Ranking    │         │
│  │  Tokenizing  │  │  Vectorizer  │  │   Top-N      │         │
│  │ Lemmatizing  │  │   (Pickle)   │  │  Candidates  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TRAINED MODELS                               │
│                    (models/ folder)                              │
│                                                                  │
│  • vectorizer.pkl     - TF-IDF Vectorizer (5000 features)      │
│  • cv_vectors.pkl     - Pre-computed CV vectors                │
│  • job_vectors.pkl    - Pre-computed Job vectors               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
INPUT (CV + Job Description)
  │
  ├─▶ [1] Text Preprocessing
  │        │
  │        ├─ Lowercase conversion
  │        ├─ Remove punctuation & numbers
  │        ├─ Tokenization
  │        ├─ Remove stopwords
  │        └─ Lemmatization
  │              │
  │              ▼
  │         "python machine learn data analys..."
  │
  ├─▶ [2] Vectorization (TF-IDF)
  │        │
  │        └─ Transform text to numerical vector
  │              │
  │              ▼
  │         [0.23, 0.45, 0.12, ..., 0.67]  (5000 dimensions)
  │
  ├─▶ [3] Similarity Computation
  │        │
  │        └─ Cosine Similarity between vectors
  │              │
  │              ▼
  │         Similarity Score: 0.8756 (87.56%)
  │
  └─▶ [4] Ranking & Recommendation
           │
           └─ Sort by score, select Top-N
                 │
                 ▼
OUTPUT: Ranked list of candidates
[
  {rank: 1, candidate: C003, score: 0.8756},
  {rank: 2, candidate: C001, score: 0.7234},
  ...
]
```

---

## 🏗️ Module Structure

### 1. **Frontend Layer** (Client-Side)

```
templates/index.html
  │
  ├─ HTML Structure
  │   ├─ Header with title
  │   ├─ Tab navigation (Manual/File/Batch)
  │   ├─ Input forms
  │   ├─ Results display
  │   └─ Loading spinner
  │
  └─ Integrated with:
       │
       ├─ static/style.css
       │    └─ Modern gradient design
       │        └─ Responsive layout
       │            └─ Animated components
       │
       └─ static/script.js
            └─ Tab switching
                └─ Form validation
                    └─ API calls (fetch)
                        └─ Results rendering
                            └─ CSV export
```

### 2. **Backend Layer** (Server-Side)

```
app.py (Flask Application)
  │
  ├─ Route Handlers
  │   ├─ GET  /              → Serve HTML
  │   ├─ GET  /api/health    → System status
  │   ├─ POST /api/recommend → Single recommendation
  │   ├─ POST /api/recommend/file → CSV upload
  │   ├─ POST /api/batch/recommend → Batch process
  │   ├─ POST /api/process/cv → Test CV processing
  │   └─ POST /api/process/job → Test job processing
  │
  ├─ Request Validation
  │   └─ Check required fields
  │       └─ Validate file formats
  │           └─ Handle errors gracefully
  │
  └─ Response Formatting
      └─ JSON with success/error
          └─ Include recommendations
              └─ Return statistics
```

### 3. **Processing Layer** (Core Logic)

```
src/recommendation_pipeline.py
  │
  ├─ CandidateRecommendationPipeline (Main Class)
  │    │
  │    ├─ __init__()
  │    │    └─ Load trained vectorizer from pickle
  │    │
  │    ├─ clean_text()
  │    │    └─ Preprocessing logic
  │    │
  │    ├─ process_cv()
  │    │    └─ Combine CV fields → Clean text
  │    │
  │    ├─ process_job()
  │    │    └─ Combine job fields → Clean text
  │    │
  │    ├─ vectorize_text()
  │    │    └─ Transform cleaned text → TF-IDF vector
  │    │
  │    ├─ compute_similarity()
  │    │    └─ Calculate cosine similarity matrix
  │    │
  │    ├─ recommend_candidates()
  │    │    └─ Single job vs multiple CVs
  │    │        └─ Return top N matches
  │    │
  │    └─ batch_recommend()
  │         └─ Multiple jobs vs multiple CVs
  │             └─ Return all matches
  │
  └─ Helper Functions
       ├─ lemmatizer (WordNet)
       └─ stopwords (English)
```

### 4. **Training Layer** (Model Preparation)

```
src/preprocessing.py
  │
  ├─ Load raw CSV data
  ├─ Combine text fields
  ├─ Apply cleaning function
  └─ Save cleaned data
       └─ results/cvs_cleaned.csv
       └─ results/jobs_cleaned.csv

src/vectorization.py
  │
  ├─ Load cleaned data
  ├─ Initialize TfidfVectorizer(max_features=5000)
  ├─ Fit on CV corpus
  ├─ Transform CVs and Jobs
  └─ Save models
       └─ models/vectorizer.pkl
       └─ models/cv_vectors.pkl
       └─ models/job_vectors.pkl

src/similarity.py
  │
  ├─ Load vectors
  ├─ Compute cosine similarity matrix
  ├─ Rank candidates
  └─ Save results
       └─ results/top_candidates.csv
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Measures               │
├─────────────────────────────────────────┤
│ 1. Input Validation                     │
│    └─ File size limits (16MB)          │
│    └─ File type validation             │
│    └─ JSON schema validation           │
│                                         │
│ 2. Error Handling                       │
│    └─ Try-catch blocks                 │
│    └─ Descriptive error messages       │
│    └─ Status code management           │
│                                         │
│ 3. Data Sanitization                    │
│    └─ Remove special characters        │
│    └─ Text normalization               │
│    └─ Safe filename handling           │
│                                         │
│ 4. Stateless Design                     │
│    └─ No persistent storage            │
│    └─ Temporary uploads cleaned        │
│    └─ Session-free operation           │
└─────────────────────────────────────────┘
```

---

## 📦 Dependencies & Stack

### Backend
- **Flask** (3.x): Web framework
- **Pandas** (2.x): Data manipulation
- **Scikit-learn** (1.x): ML library (TF-IDF, cosine similarity)
- **NLTK** (3.x): Natural language processing
- **SciPy** (1.x): Scientific computing (sparse matrices)

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (gradients, animations)
- **JavaScript (ES6+)**: Interactivity
- **Font Awesome** (6.x): Icons

### Data Format
- **CSV**: Bulk data import/export
- **JSON**: API communication
- **Pickle**: Model serialization

---

## 🗄️ Database Schema (If Extended)

```sql
-- Future enhancement: Database integration

-- Candidates Table
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(50) UNIQUE,
    skills TEXT,
    experience TEXT,
    education TEXT,
    cv_text TEXT,
    vector BYTEA,  -- Stored TF-IDF vector
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs Table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) UNIQUE,
    required_skills TEXT,
    experience_required TEXT,
    education_required TEXT,
    job_description TEXT,
    vector BYTEA,  -- Stored TF-IDF vector
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations Table
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES jobs(job_id),
    candidate_id VARCHAR(50) REFERENCES candidates(candidate_id),
    similarity_score FLOAT,
    rank INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 Processing Pipeline Flowchart

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Receive Request    │
│  (CV + Job Desc)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Validate Input    │
│  • Check required   │
│  • Check format     │
└──────┬──────────────┘
       │
       ├─── Invalid ───▶ [Return Error]
       │
       ▼ Valid
┌─────────────────────┐
│  Preprocess Text    │
│  • Clean            │
│  • Tokenize         │
│  • Lemmatize        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Load Vectorizer    │
│  (from pickle)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Vectorize Text     │
│  • CV → Vector      │
│  • Job → Vector     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Compute Similarity  │
│  (Cosine)           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Rank Candidates    │
│  • Sort by score    │
│  • Select Top-N     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Format Response    │
│  • Add ranks        │
│  • Add percentages  │
│  • Convert to JSON  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Return Results     │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│     End     │
└─────────────┘
```

---

## 📈 Scalability Considerations

### Current Design (Single Server)
```
Load: 1-100 requests/min
Users: 1-10 concurrent
Storage: File-based (pickle)
Processing: Synchronous
```

### Scalable Design (Production)
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐
│ App 1 │  │ App 2 │  │ App N │
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    └──────────┴──────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ┌──────┐     ┌──────┐
    │ Redis│     │  DB  │
    │Cache │     │(PG)  │
    └──────┘     └──────┘
```

---

## 🎯 Performance Metrics

### Current Performance
- **Preprocessing**: ~10ms per text
- **Vectorization**: ~50ms per document
- **Similarity Computation**: ~100ms for 100 CVs
- **Total Response Time**: ~500ms (average)

### Bottlenecks
1. TF-IDF transformation (CPU-bound)
2. Cosine similarity computation (memory-intensive)
3. File I/O for large CSVs

### Optimization Strategies
- Use batch processing
- Cache vectorizer in memory (✓ already done)
- Pre-compute common vectors
- Use sparse matrix operations (✓ already done)

---

## 🧪 Testing Architecture

```
tests/
  │
  ├─ unit/
  │   ├─ test_preprocessing.py
  │   ├─ test_vectorization.py
  │   └─ test_similarity.py
  │
  ├─ integration/
  │   ├─ test_pipeline.py
  │   └─ test_api_endpoints.py
  │
  └─ e2e/
      └─ test_user_flows.py
```

---

## 📊 Monitoring & Logging

```python
# Future enhancement: Logging setup

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Track:
# - API requests
# - Processing times
# - Error rates
# - Model performance
```

---

This architecture provides a solid foundation for a production-ready candidate recommendation system with clear separation of concerns and scalability options.
