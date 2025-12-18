import requests
import os

API_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_cv_upload():
    """Test CV file upload"""
    print("Testing CV upload...")
    
    # You need to have a sample CV file
    cv_file_path = "sample_cv.pdf"  # Replace with your file
    
    if not os.path.exists(cv_file_path):
        print(f"Error: {cv_file_path} not found. Please create a sample CV file.")
        return
    
    with open(cv_file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'candidate_id': 'C001',
            'name': 'John Doe'
        }
        
        response = requests.post(
            f"{API_URL}/api/upload-cv-file",
            files=files,
            data=data
        )
        
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_job_upload():
    """Test job description upload"""
    print("Testing job upload...")
    
    # You need to have a sample job file
    job_file_path = "sample_job.pdf"  # Replace with your file
    
    if not os.path.exists(job_file_path):
        print(f"Error: {job_file_path} not found. Please create a sample job file.")
        return
    
    with open(job_file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'job_id': 'J001',
            'title': 'Senior Data Scientist'
        }
        
        response = requests.post(
            f"{API_URL}/api/upload-job-file",
            files=files,
            data=data
        )
        
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_recommendations():
    """Test recommendation generation"""
    print("Testing recommendations...")
    
    data = {
        'top_n': 5
    }
    
    response = requests.post(
        f"{API_URL}/api/recommend",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Document Upload Test Suite")
    print("="*50 + "\n")
    
    # Run tests
    test_health()
    
    print("\nNote: Make sure to create sample CV and job files before running upload tests")
    print("You can create them manually or use the functions below:\n")