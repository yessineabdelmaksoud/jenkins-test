#!/usr/bin/env python3
"""Test script to validate API configuration."""

import sys
import os
from pathlib import Path 

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

def test_config():
    """Test the API configuration."""
    print("🔧 Testing AI Agents API Configuration...")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from ai_agents.deployment.api_agent.core.config import get_settings
        print("   ✅ Config import successful")
        
        from ai_agents.deployment.api_agent.main import app
        print("   ✅ FastAPI app import successful")
        
        # Test settings loading
        print("\n2. Testing settings...")
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        print(f"   📍 Host: {settings.HOST}")
        print(f"   🔌 Port: {settings.PORT}")
        print(f"   🐛 Debug: {settings.DEBUG}")
        print(f"   📝 Log Level: {settings.LOG_LEVEL}")
        
        # Test OpenAI API key
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            if settings.OPENAI_API_KEY.startswith('sk-'):
                print(f"   🔑 OpenAI API Key: ✅ Configured (starts with 'sk-')")
            else:
                print(f"   🔑 OpenAI API Key: ⚠️  Configured but doesn't start with 'sk-'")
        else:
            print(f"   🔑 OpenAI API Key: ❌ Missing or empty")
            
        # Test agent registry
        print("\n3. Testing agent registry...")
        from ai_agents.agents.registry import AGENT_REGISTRY
        print(f"   ✅ Agent registry loaded")
        print(f"   🤖 Available agents: {list(AGENT_REGISTRY.keys())}")
        
        # Test agent service
        print("\n4. Testing agent service...")
        from ai_agents.deployment.api_agent.services.agent_service import AgentService
        service = AgentService()
        print(f"   ✅ Agent service created successfully")
        
        print("\n🎉 All configuration tests passed!")
        print("\n🚀 You can now start the API server with:")
        print("   python src/ai_agents/deployment/api_agent/start_api.py")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("\n💡 Solutions:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Install dependencies: poetry install")
        print("   3. Check PYTHONPATH in .env file")
        return False
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        print("\n💡 Solutions:")
        print("   1. Create a .env file with OPENAI_API_KEY")
        print("   2. Copy .env.example to .env and update values")
        print("   3. Check that all required environment variables are set")
        return False


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
