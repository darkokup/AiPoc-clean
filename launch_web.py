"""Quick launcher for the Clinical Trial Protocol Generator web interface."""
import webbrowser
import time
import subprocess
import sys
import os

def check_server_running():
    """Check if server is already running."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    return result == 0

def main():
    print("=" * 60)
    print("Clinical Trial Protocol Generator - Web Interface Launcher")
    print("=" * 60)
    
    # Check if server is running
    if check_server_running():
        print("\n✓ Server is already running on http://localhost:8000")
    else:
        print("\n⚠ Server is not running. Starting server...")
        print("Note: Keep this window open while using the application")
        print("-" * 60)
        
        # Start the server in a subprocess
        try:
            # Start server
            subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            print("Waiting for server to start...")
            time.sleep(3)
            
            # Check if it started
            if check_server_running():
                print("✓ Server started successfully!")
            else:
                print("✗ Server failed to start. Please run manually: python main.py")
                return
                
        except Exception as e:
            print(f"✗ Error starting server: {e}")
            print("Please run manually: python main.py")
            return
    
    # Open browser
    print("\n🌐 Opening web interface in your default browser...")
    print("URL: http://localhost:8000/")
    print("\nAvailable interfaces:")
    print("  • Web UI:        http://localhost:8000/")
    print("  • API Docs:      http://localhost:8000/docs")
    print("  • ReDoc:         http://localhost:8000/redoc")
    print("  • RAG Status:    Check the web UI or run check_rag_status.py")
    
    time.sleep(1)
    webbrowser.open('http://localhost:8000/')
    
    print("\n" + "=" * 60)
    print("✅ Application launched!")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server (if started by this script)")
    print("Or close this window and manually stop: taskkill /F /IM python.exe")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        print("Server may still be running in background")
        print("To stop manually: taskkill /F /IM python.exe")

if __name__ == "__main__":
    main()
