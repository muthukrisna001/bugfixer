"""
Bugfixer Service - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from decouple import config

from .core.analyzer import CodeAnalyzer
from .core.log_analyzer import LogAnalyzer
from .core.fix_generator import FixGenerator
from .core.git_manager import GitManager
from .models.database import init_db, get_db
from .models.schemas import (
    AnalysisRequest, AnalysisResponse, 
    BugReport, FixResult, ProjectConfig
)

# Initialize FastAPI app
app = FastAPI(
    title="Bugfixer Service",
    description="Automated bug detection and fixing service",
    version="1.0.0"
)

# Mount static files for web interface
app.mount("/static", StaticFiles(directory="bugfixer/static"), name="static")

# Initialize database
init_db()

# Initialize core components
code_analyzer = CodeAnalyzer()
log_analyzer = LogAnalyzer()
fix_generator = FixGenerator()
git_manager = GitManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """
    Main dashboard for the bugfixer service
    """
    try:
        import os
        template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
        print(f"Looking for template at: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError as e:
        print(f"Template not found: {e}")
        return HTMLResponse(content="""
        <html>
        <head><title>Bugfixer Dashboard</title></head>
        <body>
        <h1>🔧 Bugfixer Dashboard</h1>
        <p>Dashboard template not found. Service is running but template is missing.</p>
        <p>API is available at <a href="/docs">/docs</a></p>
        <h2>Quick Test</h2>
        <p><a href="/api/health">Health Check</a></p>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>Bugfixer Dashboard - Error</title></head>
        <body>
        <h1>🔧 Bugfixer Dashboard</h1>
        <p>Error loading dashboard: {str(e)}</p>
        <p>API is available at <a href="/docs">/docs</a></p>
        </body>
        </html>
        """)

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_logs(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze logs and repository to find and fix bugs
    """
    try:
        print(f"Starting log analysis for {request.github_repo_url}")

        # Start background analysis
        background_tasks.add_task(
            run_log_analysis,
            request.github_repo_url,
            request.github_token,
            request.log_content,
            request.branch_name,
            request.create_pr
        )

        analysis_id = f"analysis_{abs(hash(request.github_repo_url + request.log_content[:100]))}"
        print(f"Analysis ID: {analysis_id}")

        return AnalysisResponse(
            status="started",
            message="Log analysis started in background",
            analysis_id=analysis_id
        )
    except Exception as e:
        print(f"Error in analyze_logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """
    Get the status of an ongoing analysis
    """
    # TODO: Implement status tracking
    return {"status": "running", "progress": 50}

@app.get("/api/reports", response_model=List[BugReport])
async def get_bug_reports():
    """
    Get all bug reports
    """
    # TODO: Implement database query
    return []

@app.post("/api/fix/{bug_id}")
async def fix_bug(bug_id: str, background_tasks: BackgroundTasks):
    """
    Generate and apply a fix for a specific bug
    """
    try:
        background_tasks.add_task(generate_and_apply_fix, bug_id)
        return {"status": "started", "message": f"Fix generation started for bug {bug_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "bugfixer",
        "version": "1.0.0"
    }

async def run_log_analysis(github_repo_url: str, github_token: str, log_content: str,
                          branch_name: str, create_pr: bool):
    """
    Background task to analyze logs and create fixes
    """
    try:
        print(f"Starting log analysis for {github_repo_url}")

        # 1. Analyze logs to find errors
        print("Analyzing log content...")
        errors = log_analyzer.analyze_logs(log_content)
        print(f"Found {len(errors)} errors in logs")

        if not errors:
            print("No errors found in logs")
            return

        # 2. Clone repository
        print(f"Cloning repository: {github_repo_url}")
        repo_path = await git_manager.clone_repository(github_repo_url, github_token)
        print(f"Repository cloned to: {repo_path}")

        # 3. Analyze code for each error
        fixes_applied = []
        for i, error in enumerate(errors):
            print(f"Analyzing error {i+1}/{len(errors)}: {error.error_type.value}")

            # Analyze the code to understand the error
            analysis = await code_analyzer.analyze_error(repo_path, error)

            # Generate fix suggestion
            fix_suggestion = await fix_generator.generate_fix(error, analysis)

            if fix_suggestion and fix_suggestion.confidence > 0.7:
                print(f"High confidence fix found for {error.error_type.value}")
                fixes_applied.append({
                    "error": error,
                    "fix": fix_suggestion,
                    "analysis": analysis
                })

        # 4. Create branch and apply fixes if requested
        if create_pr and fixes_applied:
            from datetime import datetime
            branch_name = f"bugfix_{datetime.now().strftime('%Y%m%d')}/main"

            print(f"Creating branch: {branch_name}")
            await git_manager.create_branch(repo_path, branch_name)

            # Apply fixes
            for fix_data in fixes_applied:
                await git_manager.apply_fix(repo_path, fix_data["fix"])

            # Commit changes
            commit_message = f"Fix {len(fixes_applied)} bugs found in logs\n\n"
            for fix_data in fixes_applied:
                commit_message += f"- Fix {fix_data['error'].error_type.value}: {fix_data['fix'].explanation}\n"

            await git_manager.commit_changes(repo_path, commit_message)

            # Create PR
            pr_url = await git_manager.create_pull_request(
                repo_path,
                github_token,
                branch_name,
                "main",
                f"Automated Bug Fixes - {datetime.now().strftime('%Y-%m-%d')}",
                commit_message
            )

            print(f"Pull request created: {pr_url}")

        print("Log analysis completed successfully")

    except Exception as e:
        print(f"Log analysis failed: {e}")
        import traceback
        traceback.print_exc()

async def generate_and_apply_fix(bug_id: str):
    """
    Background task to generate and apply fix
    """
    try:
        # Get bug details from database
        # Generate fix
        # Create branch
        # Apply fix
        # Create PR
        pass
    except Exception as e:
        print(f"Fix generation failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "bugfixer.main:app",
        host=config("BUGFIXER_HOST", default="0.0.0.0"),
        port=config("BUGFIXER_PORT", default=8001, cast=int),
        reload=config("DEBUG", default=True, cast=bool)
    )
