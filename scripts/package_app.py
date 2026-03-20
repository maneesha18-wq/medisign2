
import os
import zipfile
from pathlib import Path

def package_app(output_filename="medisign_demo.zip"):
    print(f"Packaging application to {output_filename}...")
    
    # Files/Dirs to include
    include_paths = [
        "app.py",
        "requirements.txt",
        "dataset_terms.txt",
        "modules",
        "models",
        "scripts",  # Include scripts for transparency or further dev
    ]
    
    # Files/Dirs to exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".vscode",
        "medisign_env",
        "venv",
        "env",
        "logs",
        "dataset", # Don't include the raw video dataset
        "temp_audio",
        "medisign_demo.zip"
    ]
    
    root_dir = Path(".")
    
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in include_paths:
            path = root_dir / item
            if not path.exists():
                print(f"Warning: {item} not found, skipping.")
                continue
                
            if path.is_file():
                zipf.write(path, arcname=path.name)
                print(f"Added file: {path.name}")
            elif path.is_dir():
                for file in path.rglob("*"):
                    # Check exclusions
                    if any(excluded in str(file) for excluded in exclude_patterns):
                        continue
                    if "__pycache__" in str(file):
                        continue
                        
                    arcname = file.relative_to(root_dir)
                    zipf.write(file, arcname=arcname)
                    print(f"Added: {arcname}")
                    
    print(f"Package created: {output_filename}")
    print(f"Size: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    package_app()
