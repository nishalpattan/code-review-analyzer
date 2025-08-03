#!/usr/bin/env python3
"""
Code Review Analyzer - Run Script
Supports both local and containerized deployment
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_local():
    """Run the application locally"""
    print("🚀 Starting Code Review Analyzer (Local Mode)")
    print("=" * 50)
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    
    # Install/update dependencies
    print("📦 Installing dependencies...")
    if os.name == 'nt':  # Windows
        pip_cmd = ["venv\\Scripts\\pip", "install", "-r", "requirements-local.txt"]
        python_cmd = ["venv\\Scripts\\python"]
    else:  # Unix/Linux/macOS
        pip_cmd = ["venv/bin/pip", "install", "-r", "requirements-local.txt"]
        python_cmd = ["venv/bin/python"]
    
    try:
        result = subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    
    # Set environment variables for local development
    env = os.environ.copy()
    env.update({
        "ENVIRONMENT": "development",
        "DATABASE_URL": "sqlite:///./code_analyzer.db",
        "REDIS_URL": "redis://localhost:6379",
        "SECRET_KEY": "dev-secret-key-change-in-production",
        "REPORT_EMAIL": "dev@example.com"
    })
    
    # Start the application
    print("🌟 Starting FastAPI server...")
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        if os.name == 'nt':  # Windows
            cmd = ["venv\\Scripts\\uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        else:  # Unix/Linux/macOS
            cmd = ["venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def run_docker():
    """Run the application in Docker containers"""
    print("🐳 Starting Code Review Analyzer (Docker Mode)")
    print("=" * 50)
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker", "compose", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose not found. Please install Docker first.")
        return False
    
    print("🔨 Building Docker images...")
    try:
        subprocess.run(["docker", "compose", "build"], check=True)
        print("✅ Docker images built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Docker images: {e}")
        return False
    
    print("🚀 Starting containers...")
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("\n💡 Press Ctrl+C to stop containers")
    print("=" * 50)
    
    try:
        subprocess.run(["docker", "compose", "up"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Stopping containers...")
        subprocess.run(["docker", "compose", "down"])
        print("✅ Containers stopped")
    except Exception as e:
        print(f"❌ Error running containers: {e}")
        return False
    
    return True

def run_test():
    """Run the test suite"""
    print("🧪 Running Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running, starting tests...")
            
            # Run comprehensive test
            if os.name == 'nt':  # Windows
                cmd = ["venv\\Scripts\\python", "comprehensive_test.py"]
            else:  # Unix/Linux/macOS
                cmd = ["python", "comprehensive_test.py"]
            
            subprocess.run(cmd)
        else:
            print("❌ Server is not responding properly")
            return False
    except Exception as e:
        print("❌ Server is not running. Please start the server first with:")
        print("   python run.py --local  (or)  python run.py --docker")
        return False
    
    return True

def show_status():
    """Show current system status"""
    print("📊 Code Review Analyzer - Status")
    print("=" * 50)
    
    # Check if local venv exists
    venv_exists = Path("venv").exists()
    print(f"🐍 Virtual Environment: {'✅ Available' if venv_exists else '❌ Not found'}")
    
    # Check if Docker is available
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            docker_version = result.stdout.strip()
            print(f"🐳 Docker: ✅ {docker_version}")
        else:
            print("🐳 Docker: ❌ Not available")
    except FileNotFoundError:
        print("🐳 Docker: ❌ Not installed")
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            health_data = response.json()
            print(f"🌐 Server: ✅ Running - {health_data.get('service', 'Unknown')}")
        else:
            print("🌐 Server: ⚠️  Running but unhealthy")
    except:
        print("🌐 Server: ❌ Not running")
    
    # Check database
    if Path("code_analyzer.db").exists():
        print("🗄️  Database: ✅ SQLite database found")
    else:
        print("🗄️  Database: ❌ No database found")

def main():
    parser = argparse.ArgumentParser(
        description="Code Review Analyzer - Production Ready Deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --local          # Run locally with hot reload
  python run.py --docker         # Run in Docker containers
  python run.py --test           # Run test suite
  python run.py --status         # Show system status
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--local", action="store_true", help="Run locally in development mode")
    group.add_argument("--docker", action="store_true", help="Run in Docker containers")
    group.add_argument("--test", action="store_true", help="Run the test suite")
    group.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    success = False
    if args.local:
        success = run_local()
    elif args.docker:
        success = run_docker()
    elif args.test:
        success = run_test()
    elif args.status:
        success = show_status()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
