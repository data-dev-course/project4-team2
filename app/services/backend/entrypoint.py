import uvicorn
from app import main

"""
Entry point to start this application
When the entry point is different, Please consider the relative path of packages.
"""

if __name__ == "__main__":
    uvicorn.run(main.app, host="127.0.0.1", port=8000)