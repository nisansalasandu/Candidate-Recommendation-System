# Candidate Recommendation System 🎯
**NLP-based candidate recommendation system using TF-IDF and cosine similarity to match CVs with job descriptions. Built with Python and VS Code.**

A complete full-stack web application that automatically matches candidates to job roles based on skills, experience, education, and CV content similarity.

---

## Features ✨

- **Upload CVs**: Add candidate information including skills, experience, and education
- **Upload Job Descriptions**: Add job postings with required qualifications
- **Smart Matching**: Uses TF-IDF vectorization and cosine similarity to match candidates to jobs
- **Ranked Results**: Get top candidates ranked from best to least match
- **Real-time Statistics**: Track the number of CVs and jobs in the system
- **Beautiful UI**: Modern, responsive interface with gradient design

## Technology Stack 💻

### Backend
- **Flask**: Python web framework
- **scikit-learn**: Machine learning library for TF-IDF and cosine similarity
- **NLTK**: Natural language processing for text preprocessing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Frontend
- **HTML5**: Structure
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: API integration and dynamic UI updates

## Installation & Setup 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install flask pandas scikit-learn nltk scipy
```

### Step 2: Download NLTK Data


```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
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

### 1. Upload CVs
- Browse (from computer or google drive)
- Select CV & Upload one by one
- Click "Upload CV"

### 2. Upload Job Descriptions
- Fill in job information:
  - Job Title
  - Job Description
- Click "Upload Job"

### 3. Get Recommendations
- Click "Get Recommendations"

### 4. View Results
Results are displayed with:
- **Rank badges**: Gold (#1), Silver (#2), Bronze (#3)
- **Match scores**: Percentage similarity (0-100%)
- **Color coding**: 
  - Green: High match (≥70%)
  - Yellow: Medium match (40-69%)
  - Red: Low match (<40%)
- **Candidate details**: Skills, experience, and education


## How It Works 🔍

### 1. Text Preprocessing
- Convert text to lowercase
- Remove punctuation and numbers
- Tokenize into words
- Remove stopwords (common words like "the", "is", "at")
- Apply lemmatization (reduce words to base form)

### 2. Vectorization
- Use TF-IDF (Term Frequency-Inverse Document Frequency)
- Convert text into numerical vectors
- Capture importance of words in documents

### 3. Similarity Computation
- Calculate cosine similarity between job and CV vectors
- Score ranges from 0 (no match) to 1 (perfect match)
- Rank candidates based on similarity scores

### 4. Recommendation
- Sort candidates by similarity score
- Return top N candidates for each job
- Display with detailed information

## Features in Detail 🌟

### Real-time Updates
- Statistics automatically refresh every 10 seconds
- Instant feedback on form submissions
- Dynamic results display

### Data Validation
- Required field validation
- Unique ID enforcement
- Error handling and user feedback

### User-Friendly Interface
- Responsive design for all devices
- Intuitive form layouts
- Color-coded results for easy interpretation
- Hover effects and smooth animations

### Data Management
- Clear all data option
- View current statistics
- Filter recommendations by job ID




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
