#!/usr/bin/env python3
"""
Bugfixer Service Runner
Main entry point for the bugfixer service
"""
import uvicorn
import os
import sys
from decouple import config

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the bugfixer service"""
    host = config("BUGFIXER_HOST", default="0.0.0.0")
    port = config("BUGFIXER_PORT", default=8001, cast=int)
    debug = config("DEBUG", default=True, cast=bool)
    
    print("🔧 Starting Bugfixer Service...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"🌐 Dashboard: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "bugfixer.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )

if __name__ == "__main__":
    main()
