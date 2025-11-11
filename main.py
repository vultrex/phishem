#!/usr/bin/env python3
"""
Discord Anti-Phishing Bot - Main Entry Point
This file serves as the entry point for the Docker container.
"""

import sys
import os
from pathlib import Path

# Add the project root and src to Python path
project_root = Path(__file__).parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

# Import and run the main bot
if __name__ == "__main__":
    try:
        # Import the main function from the core module
        from src.core.main import main
        
        # Run the bot
        import asyncio
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Bot shutdown requested")
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)
