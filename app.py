"""
Flask Backend API for Candidate Recommendation System
Provides endpoints for uploading CVs, Job Descriptions, and getting recommendations
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json
from src.recommendation_pipeline import CandidateRecommendationPipeline

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the recommendation pipeline
try:
    pipeline = CandidateRecommendationPipeline(vectorizer_path='models/vectorizer.pkl')
    print("✓ Recommendation pipeline initialized successfully")
except Exception as e:
    print(f"✗ Error initializing pipeline: {str(e)}")
    pipeline = None

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline_loaded': pipeline is not None
    })


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint
    Accepts job description and list of CVs, returns ranked candidates
    
    Expected JSON format:
    {
        "job": {
            "required_skills": "...",
            "experience_required": "...",
            "education_required": "...",
            "job_description": "..."
        },
        "candidates": [
            {
                "candidate_id": "...",
                "skills": "...",
                "experience": "...",
                "education": "...",
                "cv_text": "..."
            }
        ],
        "top_n": 5
    }
    """
    if pipeline is None:
        return jsonify({'error': 'Recommendation pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'job' not in data or 'candidates' not in data:
            return jsonify({'error': 'Invalid request format. Required: job, candidates'}), 400
        
        job_data = data['job']
        candidates_data = data['candidates']
        top_n = data.get('top_n', 5)
        
        if len(candidates_data) == 0:
            return jsonify({'error': 'No candidates provided'}), 400
        
        # Get recommendations
        recommendations = pipeline.recommend_candidates(
            job_data=job_data,
            cv_data_list=candidates_data,
            top_n=min(top_n, len(candidates_data))
        )
        
        return jsonify({
            'success': True,
            'total_candidates': len(candidates_data),
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': f'Recommendation failed: {str(e)}'}), 500


@app.route('/api/recommend/file', methods=['POST'])
def recommend_from_files():
    """
    Recommendation endpoint for CSV file uploads
    Accepts CSV files for CVs and Jobs
    
    Expected form data:
    - cvs_file: CSV file with candidate data
    - jobs_file: CSV file with job descriptions
    - top_n: Number of top candidates (optional, default=5)
    """
    if pipeline is None:
        return jsonify({'error': 'Recommendation pipeline not initialized'}), 500
    
    try:
        # Check if files are present
        if 'cvs_file' not in request.files or 'jobs_file' not in request.files:
            return jsonify({'error': 'Both cvs_file and jobs_file are required'}), 400
        
        cvs_file = request.files['cvs_file']
        jobs_file = request.files['jobs_file']
        top_n = int(request.form.get('top_n', 5))
        
        if cvs_file.filename == '' or jobs_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Read CSV files
        cvs_df = pd.read_csv(cvs_file)
        jobs_df = pd.read_csv(jobs_file)
        
        # Validate required columns for CVs
        required_cv_cols = ['candidate_id']
        if not all(col in cvs_df.columns for col in required_cv_cols):
            return jsonify({'error': f'CVs CSV must contain: {required_cv_cols}'}), 400
        
        # Validate required columns for Jobs
        required_job_cols = ['job_id']
        if not all(col in jobs_df.columns for col in required_job_cols):
            return jsonify({'error': f'Jobs CSV must contain: {required_job_cols}'}), 400
        
        # Batch process recommendations
        recommendations_df = pipeline.batch_recommend(jobs_df, cvs_df, top_n=top_n)
        
        # Convert to JSON-friendly format
        recommendations = recommendations_df.to_dict('records')
        
        return jsonify({
            'success': True,
            'total_jobs': len(jobs_df),
            'total_candidates': len(cvs_df),
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': f'File processing failed: {str(e)}'}), 500


@app.route('/api/process/cv', methods=['POST'])
def process_single_cv():
    """
    Process a single CV and return cleaned text
    Useful for debugging/testing
    """
    if pipeline is None:
        return jsonify({'error': 'Pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        
        cleaned_text = pipeline.process_cv(
            skills=data.get('skills', ''),
            experience=data.get('experience', ''),
            education=data.get('education', ''),
            cv_text=data.get('cv_text', '')
        )
        
        return jsonify({
            'success': True,
            'cleaned_text': cleaned_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process/job', methods=['POST'])
def process_single_job():
    """
    Process a single job description and return cleaned text
    Useful for debugging/testing
    """
    if pipeline is None:
        return jsonify({'error': 'Pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        
        cleaned_text = pipeline.process_job(
            required_skills=data.get('required_skills', ''),
            experience_required=data.get('experience_required', ''),
            education_required=data.get('education_required', ''),
            job_description=data.get('job_description', '')
        )
        
        return jsonify({
            'success': True,
            'cleaned_text': cleaned_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch/recommend', methods=['POST'])
def batch_recommend():
    """
    Batch recommendation for multiple jobs and candidates
    More efficient than calling /api/recommend multiple times
    """
    if pipeline is None:
        return jsonify({'error': 'Pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        candidates = data.get('candidates', [])
        top_n = data.get('top_n', 5)
        
        if not jobs or not candidates:
            return jsonify({'error': 'Both jobs and candidates are required'}), 400
        
        # Convert to DataFrames
        jobs_df = pd.DataFrame(jobs)
        cvs_df = pd.DataFrame(candidates)
        
        # Process batch
        recommendations_df = pipeline.batch_recommend(jobs_df, cvs_df, top_n=top_n)
        
        return jsonify({
            'success': True,
            'total_jobs': len(jobs),
            'total_candidates': len(candidates),
            'recommendations': recommendations_df.to_dict('records')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("   Candidate Recommendation System - Backend Server")
    print("="*60)
    print("\nEndpoints available:")
    print("  GET  /                      - Web interface")
    print("  GET  /api/health            - Health check")
    print("  POST /api/recommend         - Single job recommendation")
    print("  POST /api/recommend/file    - Upload CSV files")
    print("  POST /api/batch/recommend   - Batch recommendations")
    print("  POST /api/process/cv        - Process single CV")
    print("  POST /api/process/job       - Process single job")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
