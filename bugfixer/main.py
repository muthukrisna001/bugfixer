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
import uuid
import asyncio
import json
from datetime import datetime
from decouple import config

from bugfixer.core.analyzer import CodeAnalyzer
from bugfixer.core.log_analyzer import LogAnalyzer
from bugfixer.core.free_ai_analyzer import FreeAIAnalyzer
from bugfixer.models.database import init_db, get_db
from bugfixer.models.schemas import (
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
ai_analyzer = FreeAIAnalyzer()  # Free AI integration for analysis

# Global storage for analysis progress and results
analysis_progress = {}
analysis_results = {}

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

        # Generate unique analysis ID
        analysis_id = f"analysis_{abs(hash(request.github_repo_url + request.log_content[:100]))}"
        print(f"Generated Analysis ID: {analysis_id}")

        # Initialize progress tracking immediately
        analysis_progress[analysis_id] = {
            "status": "initializing",
            "message": "Analysis request received, starting background task...",
            "progress": 0,
            "current_step": "initialization",
            "total_steps": 4,  # Simplified: parse → analyze → complete
            "errors_found": 0,
            "issues_analyzed": 0,
            "timestamp": datetime.now().isoformat()
        }
        print(f"Initialized progress tracking for: {analysis_id}")

        # Start background analysis with progress tracking
        background_tasks.add_task(
            run_log_analysis,
            request.github_repo_url,
            request.github_token,
            request.log_content,
            analysis_id
        )

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
    if analysis_id in analysis_progress:
        return analysis_progress[analysis_id]
    else:
        return {"status": "not_found", "message": "Analysis not found"}

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

@app.get("/api/progress/{analysis_id}")
async def get_analysis_progress(analysis_id: str):
    """
    Get real-time progress of analysis
    """
    print(f"Progress request for analysis_id: {analysis_id}")
    print(f"Available analysis IDs: {list(analysis_progress.keys())}")

    if analysis_id not in analysis_progress:
        print(f"Analysis {analysis_id} not found in progress tracking")
        # Return a proper response instead of raising 404
        return {
            "status": "not_found",
            "message": "Analysis not found or not started yet",
            "progress": 0,
            "current_step": "unknown"
        }

    progress_data = analysis_progress[analysis_id]
    print(f"Returning progress: {progress_data}")
    return progress_data

@app.get("/api/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """
    Get analysis results including proposed fixes
    """
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")

    return analysis_results[analysis_id]

@app.post("/api/approve-fixes/{analysis_id}")
async def approve_fixes(analysis_id: str, approved_fixes: List[str]):
    """
    Approve specific fixes and proceed with commit/PR
    """
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Update progress
    analysis_progress[analysis_id].update({
        "status": "applying_fixes",
        "message": "Applying approved fixes...",
        "progress": 80
    })

    # Start background task to apply approved fixes
    background_tasks = BackgroundTasks()
    background_tasks.add_task(apply_approved_fixes, analysis_id, approved_fixes)

    return {
        "status": "success",
        "message": "Approved fixes are being applied",
        "analysis_id": analysis_id
    }

async def run_log_analysis(github_repo_url: str, github_token: str, log_content: str, analysis_id: str = None):
    """
    Simplified background task to analyze logs with GitHub Copilot - no fix generation
    """
    if not analysis_id:
        analysis_id = str(uuid.uuid4())

    # Update progress tracking (don't overwrite if already exists)
    if analysis_id not in analysis_progress:
        analysis_progress[analysis_id] = {
            "status": "starting",
            "message": "Initializing analysis...",
            "progress": 0,
            "current_step": "initialization",
            "total_steps": 4,  # Reduced steps: parse, analyze, complete
            "errors_found": 0,
            "issues_analyzed": 0,
            "timestamp": datetime.now().isoformat()
        }

    # Update to show background task has started
    analysis_progress[analysis_id].update({
        "status": "starting",
        "message": "Background analysis task started...",
        "progress": 5,
        "current_step": "initialization"
    })

    try:
        print(f"Background task started for analysis_id: {analysis_id}")
        print(f"Starting log analysis for {github_repo_url}")

        # Step 1: Parse log content
        print("Step 1: Parsing logs...")
        analysis_progress[analysis_id].update({
            "status": "parsing_logs",
            "message": "Parsing log content for errors...",
            "progress": 20,
            "current_step": "log_parsing"
        })

        print("Parsing log content...")
        errors = log_analyzer.analyze_logs(log_content)
        print(f"Found {len(errors)} errors in logs")

        analysis_progress[analysis_id].update({
            "errors_found": len(errors),
            "message": f"Found {len(errors)} errors in logs"
        })

        if not errors:
            analysis_progress[analysis_id].update({
                "status": "completed",
                "message": "No errors found in logs",
                "progress": 100,
                "issues_found": []
            })
            return

        # Step 2: Get codebase context (optional - for better analysis)
        analysis_progress[analysis_id].update({
            "status": "fetching_codebase",
            "message": "Fetching codebase context...",
            "progress": 40,
            "current_step": "codebase_context"
        })

        codebase_context = "No codebase context available"
        if github_repo_url and github_repo_url != "https://github.com/octocat/Hello-World.git":
            try:
                codebase_context = f"Repository: {github_repo_url}"
                print(f"Using codebase context: {codebase_context}")
            except Exception as e:
                print(f"Could not fetch codebase context: {e}")

        # Step 3: Analyze each error with Free AI
        analysis_progress[analysis_id].update({
            "status": "analyzing_with_ai",
            "message": "Analyzing errors with AI...",
            "progress": 60,
            "current_step": "ai_analysis"
        })

        analyzed_issues = []
        for i, error in enumerate(errors):
            progress_percent = 60 + (30 * (i + 1) / len(errors))  # 60-90%
            analysis_progress[analysis_id].update({
                "message": f"Analyzing error {i+1}/{len(errors)}: {error.error_type.value}",
                "progress": int(progress_percent)
            })

            print(f"Analyzing error {i+1}/{len(errors)} with AI: {error.error_type.value}")

            # Convert error to dict for AI analysis
            error_dict = {
                "error_type": error.error_type.value,
                "error_message": error.error_message,
                "file_path": error.file_path,
                "line_number": error.line_number,
                "traceback": error.traceback,
                "timestamp": error.timestamp
            }

            # Get AI analysis using free models
            ai_result = await ai_analyzer.analyze_error_with_free_ai(error_dict, codebase_context)

            analyzed_issues.append({
                "original_error": error_dict,
                "ai_analysis": ai_result,
                "issue_id": str(uuid.uuid4())
            })

        # Step 4: Complete analysis
        analysis_progress[analysis_id].update({
            "status": "completed",
            "message": f"Analysis complete! Found {len(analyzed_issues)} issues",
            "progress": 100,
            "issues_found": analyzed_issues,
            "total_issues": len(analyzed_issues),
            "timestamp": datetime.now().isoformat()
        })

        # Store results
        analysis_results[analysis_id] = {
            "issues": analyzed_issues,
            "summary": {
                "total_errors": len(errors),
                "total_issues": len(analyzed_issues),
                "repository": github_repo_url,
                "analyzed_at": datetime.now().isoformat()
            }
        }

        print(f"✅ Analysis completed for {analysis_id}: {len(analyzed_issues)} issues found")

    except Exception as e:
        print(f"Log analysis failed: {e}")
        analysis_progress[analysis_id].update({
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "progress": 0,
            "error": str(e)
        })
        import traceback
        traceback.print_exc()

# Removed apply_approved_fixes function - no longer needed for analysis-only workflow

@app.get("/api/issues/{analysis_id}")
async def get_analysis_issues(analysis_id: str):
    """Get analyzed issues for an analysis"""

    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_results[analysis_id]

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
