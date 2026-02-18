#!/usr/bin/env python
"""
Run the Ramadan Countdown application
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Ramadan Countdown Web App...")
    print("Open http://localhost:8000 in your browser")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
