import zipfile
import os

zip_path = r'c:\Users\vishn\OneDrive\Desktop\New folder\medisign\medisign_demo.zip'
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        dataset_files = [name for name in zip_ref.namelist() if 'dataset' in name.lower()]
        for name in dataset_files[:20]:
            print(name)
        print(f"Total dataset files in zip: {len(dataset_files)}")
else:
    print(f"File not found: {zip_path}")
