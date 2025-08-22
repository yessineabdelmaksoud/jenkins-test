
"""Script to start the AI Agents API server."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"📄 Loaded environment from: {env_file}")
else:
    print(f"⚠️ .env file not found at: {env_file}")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import uvicorn
from ai_agents.deployment.api_agent.main import app
from ai_agents.deployment.api_agent.core.config import get_settings


def main():
    """Start the API server."""
    try:
        settings = get_settings()

        print(f"🚀 Starting AI Agents API server...")
        print(f"📍 Host: {settings.HOST}")
        print(f"🔌 Port: {settings.PORT}")
        print(f"🐛 Debug: {settings.DEBUG}")
        print(f"🔑 OpenAI API Key: {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Missing'}")
        print(f"� Jenkins URL: {os.getenv('JENKINS_URL', '❌ Not set')}")
        print(f"👤 Jenkins User: {os.getenv('JENKINS_USER', '❌ Not set')}")
        print(f"🔑 Jenkins Token: {'✅ Configured' if os.getenv('JENKINS_TOKEN') else '❌ Not set'}")
        print(f"📧 Email Config: {'✅ Configured' if os.getenv('EMAIL_SENDER') and os.getenv('EMAIL_PASSWORD') else '❌ Not set'}")
        print(f"💬 Slack Config: {'✅ Configured' if os.getenv('SLACK_WEBHOOK_URL') else '❌ Not set'}")
        print(f"�📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"🔄 Alternative docs: http://{settings.HOST}:{settings.PORT}/redoc")

        uvicorn.run(
            "ai_agents.deployment.api_agent.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )

    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print("\n💡 Common solutions:")
        print("   1. Make sure you have a .env file with OPENAI_API_KEY=your-key-here")
        print("   2. Check that all required dependencies are installed: poetry install")
        print("   3. Verify your OpenAI API key is valid")
        print("\n📝 Example .env file:")
        print("   PYTHONPATH=src")
        print("   OPENAI_API_KEY=sk-your-openai-api-key-here")
        print("   DEBUG=true")
        sys.exit(1)


if __name__ == "__main__":
    main()
