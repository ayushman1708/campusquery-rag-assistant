# CampusQuery Development Log

## Day 1 — Project Foundation

### Goal
Set up the CampusQuery repository and create a working FastAPI backend foundation.

### Completed
- Created a professional project folder structure
- Added Git ignore rules for virtual environments, secrets, PDFs, logs, and generated files
- Created Python dependency requirements
- Created and activated a Python virtual environment
- Installed FastAPI and python-dotenv
- Built a root API endpoint
- Built and tested a health-check endpoint
- Verified the backend through FastAPI interactive documentation

### What I learned
- FastAPI creates backend API endpoints using Python functions and route decorators
- A health-check endpoint verifies that a backend service is running
- A virtual environment isolates project dependencies from other Python projects
- pip installs Python packages inside the active virtual environment
- `.gitignore` prevents secret and unnecessary files from being uploaded to GitHub

### Next Step
Create document models and implement the first PDF upload endpoint.