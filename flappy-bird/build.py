"""
Convenience script to build the WebAssembly browser release using pygbag.
Usage:
    python build.py
"""
import sys
import subprocess
import os

def build():
    print("Building Flappy Bird WebAssembly package with pygbag...")
    os.makedirs("build/web", exist_ok=True)
    cmd = [sys.executable, "-m", "pygbag", "--build", "."]
    try:
        subprocess.check_call(cmd)
        print("\n[OK] Build complete! Web build is available at 'build/web/'")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    build()
