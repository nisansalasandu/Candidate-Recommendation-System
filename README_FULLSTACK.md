# Candidate Recommendation System 🎯

A full-stack web application that uses Machine Learning to match candidates with job descriptions based on skills, experience, and education.

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

## Project Structure 📁

```
Candidate-Recommendation-System/
│
├── app.py                      # Flask backend API
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/                        # Source code for ML pipeline
│   ├── preprocessing.py        # Text cleaning and preprocessing
│   ├── vectorization.py        # TF-IDF vectorization
│   └── similarity.py           # Similarity computation
│
├── templates/                  # HTML templates
│   └── index.html             # Main web interface
│
├── static/                     # Static assets
│   ├── style.css              # CSS styling
│   └── script.js              # JavaScript logic
│
├── data/                       # Training data
│   ├── cvs_100.csv            # Sample CV data
│   └── jobs_10.csv            # Sample job data
│
├── models/                     # Saved ML models
│   ├── vectorizer.pkl         # TF-IDF vectorizer
│   ├── cv_vectors.pkl         # CV vectors
│   └── job_vectors.pkl        # Job vectors
│
└── results/                    # Output files
    ├── cvs_cleaned.csv        # Preprocessed CVs
    ├── jobs_cleaned.csv       # Preprocessed jobs
    └── top_candidates.csv     # Recommendations
```

## Installation & Setup 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Download NLTK Data
The app will automatically download required NLTK data on first run, but you can also do it manually:

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
```

### Step 3: Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

## Usage Guide 📖

### 1. Upload CVs
- Fill in candidate information:
  - Candidate ID (unique identifier)
  - Full Name
  - Skills (e.g., "Python, Machine Learning, Flask")
  - Experience (work history and duration)
  - Education (degrees and institutions)
  - Additional CV details (optional)
- Click "Upload CV"

### 2. Upload Job Descriptions
- Fill in job information:
  - Job ID (unique identifier)
  - Job Title
  - Required Skills
  - Experience Required
  - Education Required
  - Job Description
- Click "Upload Job"

### 3. Get Recommendations
- **For All Jobs**: Leave "Job ID" field empty
- **For Specific Job**: Enter the job ID
- Set the number of top candidates (default: 5)
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

## API Endpoints 🔌

### Upload CV
```
POST /api/upload-cv
Content-Type: application/json

{
  "candidate_id": "C001",
  "name": "John Doe",
  "skills": "Python, Machine Learning, Data Analysis",
  "experience": "5 years as Data Scientist",
  "education": "Master's in Computer Science",
  "cv_text": "Additional details..."
}
```

### Upload Job
```
POST /api/upload-job
Content-Type: application/json

{
  "job_id": "J001",
  "title": "Senior Data Scientist",
  "required_skills": "Python, Machine Learning, Statistics",
  "experience_required": "5+ years in data science",
  "education_required": "Master's degree",
  "job_description": "We are looking for..."
}
```

### Get Recommendations
```
POST /api/recommend
Content-Type: application/json

{
  "job_id": "J001",  // optional, null for all jobs
  "top_n": 5         // number of top candidates
}
```

### Get All CVs
```
GET /api/cvs
```

### Get All Jobs
```
GET /api/jobs
```

### Clear All Data
```
POST /api/clear
```

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

## Troubleshooting 🔧

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### NLTK Download Issues
If NLTK data doesn't download automatically:
```python
import nltk
nltk.download('all')
```

### CORS Issues
The app includes CORS support. If you still face issues:
- Check if Flask-CORS is installed
- Verify the API_URL in `script.js` matches your server

## Future Enhancements 🚀

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] CV file upload (PDF, DOCX parsing)
- [ ] Advanced filtering and search
- [ ] Email notifications for matches
- [ ] Export recommendations to CSV/PDF
- [ ] Batch upload functionality
- [ ] Dashboard with analytics and charts
- [ ] A/B testing for different matching algorithms

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is open source and available under the MIT License.

## Contact 📧

For questions or support, please open an issue in the repository.

---

**Made with ❤️ for better candidate-job matching**
