"""Main entry point for Agentic RAG Chatbot"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.streamlit_app import StreamlitApp

def main():
    """Main function to run the application"""
    print("🚀 Starting Agentic RAG Chatbot...")
    print("📝 Make sure to set GOOGLE_API_KEY environment variable for full LLM functionality")
    print("🌐 Access the application at: http://localhost:8501")
    
    # Create and run the Streamlit app
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()