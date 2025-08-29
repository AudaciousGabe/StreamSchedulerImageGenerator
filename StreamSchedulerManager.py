#!/usr/bin/env python3
"""
StreamSchedulerManager.py
Opens the StreamSchedulerImageGenerator.html file when the script is executed.
"""

import webbrowser
import os
import sys
from pathlib import Path

def open_html_file():
    """
    Opens the StreamSchedulerImageGenerator.html file in the default web browser.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Construct the path to the HTML file
        html_file = script_dir / "StreamSchedulerImageGenerator.html"
        
        # Check if the HTML file exists
        if not html_file.exists():
            print(f"Error: HTML file not found at {html_file}")
            return False
        
        # Convert to absolute path and file URL
        file_url = html_file.absolute().as_uri()
        
        print(f"Opening StreamSchedulerImageGenerator.html...")
        print(f"Location: {html_file}")
        
        # Open the HTML file in the default browser
        webbrowser.open(file_url)
        print("HTML file opened successfully in your browser!")
        return True
        
    except Exception as e:
        print(f"Error opening HTML file: {e}")
        return False

def main():
    """
    Main function that executes when the script is run.
    """
    print("StreamSchedulerManager Started")
    print("=" * 50)
    
    # Open the HTML file
    if open_html_file():
        print("\nThe StreamSchedulerImageGenerator has been opened.")
        print("\nYou can now use the web interface to generate schedule images.")
        
        # Keep the script running if needed
        print("\nPress Enter to exit this manager...")
        input()
    else:
        print("\nFailed to open the StreamSchedulerImageGenerator.")
        print("Please ensure StreamSchedulerImageGenerator.html exists in the same directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()
