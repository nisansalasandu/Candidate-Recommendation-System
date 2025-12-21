// script.js - Frontend JavaScript for Candidate Recommendation System

let candidateCount = 0;
let recommendationsData = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Add first candidate form by default
    addCandidate();
    checkHealth();
});

// Check API health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (!data.pipeline_loaded) {
            showError('Warning: Recommendation pipeline not fully loaded. Some features may not work.');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.closest('.tab-button').classList.add('active');
    
    // Hide results when switching tabs
    document.getElementById('results-section').style.display = 'none';
}

// Add candidate form
function addCandidate() {
    candidateCount++;
    const container = document.getElementById('candidates-container');
    
    const candidateForm = document.createElement('div');
    candidateForm.className = 'candidate-form';
    candidateForm.id = `candidate-${candidateCount}`;
    candidateForm.innerHTML = `
        <div class="candidate-header">
            <h3><i class="fas fa-user"></i> Candidate ${candidateCount}</h3>
            <button class="btn-remove" onclick="removeCandidate(${candidateCount})">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="form-group">
            <label>Candidate ID *</label>
            <input type="text" id="candidate-id-${candidateCount}" placeholder="C${candidateCount.toString().padStart(3, '0')}" value="C${candidateCount.toString().padStart(3, '0')}">
        </div>
        <div class="form-group">
            <label>Skills *</label>
            <textarea id="candidate-skills-${candidateCount}" placeholder="e.g., Python, Java, Machine Learning"></textarea>
        </div>
        <div class="form-group">
            <label>Experience</label>
            <textarea id="candidate-experience-${candidateCount}" placeholder="e.g., 3 years as Software Developer"></textarea>
        </div>
        <div class="form-group">
            <label>Education</label>
            <textarea id="candidate-education-${candidateCount}" placeholder="e.g., BS in Computer Science"></textarea>
        </div>
        <div class="form-group">
            <label>CV Text / Additional Info</label>
            <textarea id="candidate-cv-${candidateCount}" rows="3" placeholder="Full CV text or additional information"></textarea>
        </div>
    `;
    
    container.appendChild(candidateForm);
}

// Remove candidate form
function removeCandidate(id) {
    const candidate = document.getElementById(`candidate-${id}`);
    if (candidate) {
        candidate.remove();
    }
}

// Get recommendations (Manual Input)
async function getRecommendations() {
    try {
        showLoading();
        hideError();
        
        // Collect job data
        const jobData = {
            required_skills: document.getElementById('job-skills').value,
            experience_required: document.getElementById('job-experience').value,
            education_required: document.getElementById('job-education').value,
            job_description: document.getElementById('job-description').value
        };
        
        // Validate job data
        if (!jobData.required_skills && !jobData.job_description) {
            hideLoading();
            showError('Please provide at least job skills or job description');
            return;
        }
        
        // Collect candidates data
        const candidates = [];
        const candidateForms = document.querySelectorAll('.candidate-form');
        
        candidateForms.forEach(form => {
            const id = form.id.split('-')[1];
            const candidateData = {
                candidate_id: document.getElementById(`candidate-id-${id}`).value,
                skills: document.getElementById(`candidate-skills-${id}`).value,
                experience: document.getElementById(`candidate-experience-${id}`).value,
                education: document.getElementById(`candidate-education-${id}`).value,
                cv_text: document.getElementById(`candidate-cv-${id}`).value
            };
            
            // Only add if at least one field is filled
            if (candidateData.skills || candidateData.cv_text) {
                candidates.push(candidateData);
            }
        });
        
        if (candidates.length === 0) {
            hideLoading();
            showError('Please add at least one candidate with skills or CV text');
            return;
        }
        
        const topN = parseInt(document.getElementById('top-n').value);
        
        // Send request
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job: jobData,
                candidates: candidates,
                top_n: topN
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        hideLoading();
        displayResults(data);
        
    } catch (error) {
        hideLoading();
        showError(`Error: ${error.message}`);
    }
}

// Handle file selection
function handleFileSelect(type) {
    const fileInput = document.getElementById(`${type}-file`);
    const fileName = document.getElementById(`${type}-file-name`);
    
    if (fileInput.files.length > 0) {
        fileName.textContent = `✓ ${fileInput.files[0].name}`;
        fileName.style.color = '#27ae60';
    }
}

// Upload files
async function uploadFiles() {
    try {
        showLoading();
        hideError();
        
        const cvsFile = document.getElementById('cvs-file').files[0];
        const jobsFile = document.getElementById('jobs-file').files[0];
        
        if (!cvsFile || !jobsFile) {
            hideLoading();
            showError('Please select both CVs and Jobs CSV files');
            return;
        }
        
        const topN = parseInt(document.getElementById('file-top-n').value);
        
        const formData = new FormData();
        formData.append('cvs_file', cvsFile);
        formData.append('jobs_file', jobsFile);
        formData.append('top_n', topN);
        
        const response = await fetch('/api/recommend/file', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        
        hideLoading();
        displayResults(data);
        
    } catch (error) {
        hideLoading();
        showError(`Error: ${error.message}`);
    }
}

// Batch process
async function batchProcess() {
    try {
        showLoading();
        hideError();
        
        const jobsText = document.getElementById('batch-jobs').value;
        const candidatesText = document.getElementById('batch-candidates').value;
        
        if (!jobsText || !candidatesText) {
            hideLoading();
            showError('Please provide both jobs and candidates JSON data');
            return;
        }
        
        // Parse JSON
        let jobs, candidates;
        try {
            jobs = JSON.parse(jobsText);
            candidates = JSON.parse(candidatesText);
        } catch (e) {
            hideLoading();
            showError('Invalid JSON format. Please check your input.');
            return;
        }
        
        const topN = parseInt(document.getElementById('batch-top-n').value);
        
        const response = await fetch('/api/batch/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jobs: jobs,
                candidates: candidates,
                top_n: topN
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Batch process failed');
        }
        
        hideLoading();
        displayResults(data);
        
    } catch (error) {
        hideLoading();
        showError(`Error: ${error.message}`);
    }
}

// Display results
function displayResults(data) {
    const resultsSection = document.getElementById('results-section');
    const statsContainer = document.getElementById('results-stats');
    const resultsContainer = document.getElementById('results-container');
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Handle both old format (recommendations) and new format (jobs)
    const jobs = data.jobs || [];
    const totalJobs = data.total_jobs || jobs.length || 1;
    const totalCandidates = data.total_candidates || 0;
    
    // Count total matches across all jobs
    let totalMatches = 0;
    if (jobs.length > 0) {
        totalMatches = jobs.reduce((sum, job) => sum + (job.candidates ? job.candidates.length : 0), 0);
        recommendationsData = jobs.flatMap(job => 
            (job.candidates || []).map(c => ({...c, job_id: job.job_id, job_title: job.job_title}))
        );
    } else if (data.recommendations) {
        // Fallback for old format
        recommendationsData = data.recommendations;
        totalMatches = recommendationsData.length;
    }
    
    // Display stats
    statsContainer.innerHTML = `
        <div class="stat-card">
            <i class="fas fa-briefcase"></i>
            <div class="stat-value">${totalJobs}</div>
            <div class="stat-label">Job${totalJobs > 1 ? 's' : ''} Processed</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-users"></i>
            <div class="stat-value">${totalCandidates}</div>
            <div class="stat-label">Total Candidates</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-star"></i>
            <div class="stat-value">${totalMatches}</div>
            <div class="stat-label">Total Matches</div>
        </div>
    `;
    
    // Display recommendations grouped by job
    if (jobs.length === 0 && (!recommendationsData || recommendationsData.length === 0)) {
        resultsContainer.innerHTML = '<p class="no-results">No recommendations found</p>';
        return;
    }
    
    let html = '';
    
    // Display results grouped by job
    if (jobs.length > 0) {
        jobs.forEach((job, jobIndex) => {
            const candidates = job.candidates || [];
            
            html += `
                <div class="job-results">
                    <div class="job-header">
                        <h3><i class="fas fa-briefcase"></i> ${job.job_title}</h3>
                        <span class="job-id">Job ID: ${job.job_id}</span>
                        <span class="match-count">${candidates.length} Candidate${candidates.length !== 1 ? 's' : ''} Matched</span>
                    </div>
                    <div class="recommendations-grid">
            `;
            
            candidates.forEach(candidate => {
                const scorePercent = candidate.match_percentage || (candidate.similarity_score * 100);
                const scoreColor = scorePercent >= 70 ? '#27ae60' : scorePercent >= 50 ? '#f39c12' : '#e74c3c';
                
                html += `
                    <div class="recommendation-card">
                        <div class="rank-badge rank-${candidate.rank}">
                            <i class="fas fa-medal"></i> Rank ${candidate.rank}
                        </div>
                        <div class="candidate-info">
                            <h4><i class="fas fa-user"></i> ${candidate.name || candidate.candidate_id}</h4>
                            <p class="candidate-id">ID: ${candidate.candidate_id}</p>
                            <div class="score-container">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${scorePercent}%; background: ${scoreColor}"></div>
                                </div>
                                <div class="score-text">
                                    <span class="score-value" style="color: ${scoreColor}">${scorePercent.toFixed(2)}%</span>
                                    <span class="score-label">Match Score</span>
                                </div>
                            </div>
                            <div class="similarity-score">
                                Cosine Similarity: ${candidate.similarity_score.toFixed(4)}
                            </div>
                            ${candidate.summary ? `<div class="candidate-summary">${candidate.summary}</div>` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
    }
    
    resultsContainer.innerHTML = html;
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Export results to CSV
function exportResults() {
    if (recommendationsData.length === 0) {
        showError('No results to export');
        return;
    }
    
    // Create CSV content
    const headers = Object.keys(recommendationsData[0]);
    const csvContent = [
        headers.join(','),
        ...recommendationsData.map(row => 
            headers.map(header => {
                const value = row[header];
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value}"` 
                    : value;
            }).join(',')
        )
    ].join('\n');
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recommendations_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// UI Helper functions
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}
