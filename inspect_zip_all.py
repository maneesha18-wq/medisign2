import zipfile
import os

zip_path = r'c:\Users\vishn\OneDrive\Desktop\New folder\medisign\medisign_demo.zip'
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            print(name)
        print(f"Total files in zip: {len(zip_ref.namelist())}")
else:
    print(f"File not found: {zip_path}")
