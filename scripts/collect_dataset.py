
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.data_acquisition import DataAcquisition

def load_terms(filepath="dataset_terms.txt"):
    """Load medical terms from a text file."""
    if not os.path.exists(filepath):
        print(f"Error: Terms file '{filepath}' not found.")
        return []
    with open(filepath, "r") as f:
        terms = [line.strip() for line in f if line.strip()]
    return terms

def main():
    terms = load_terms()
    if not terms:
        return
    
    print(f"Loaded {len(terms)} medical terms.")
    
    recorder = DataAcquisition()
    
    # Interactive session
    for term in terms:
        print(f"\nProcessing term: {term}")
        print("Press Enter to start collection for this term, or 'type' to skip...")
        # Simple input to pause
        choice = input(f"Collect samples for '{term}'? [Y/n]: ").lower()
        if choice == 'n':
            continue
            
        print(f"Starting capture for {term}...")
        # Since DataAcquisition has interactive_session, we can use it?
        # But wait, my implementation of interactive_session above was a bit skeletal.
        # Let's verify data_acquisition really has interactive_session.
        # Yes, I wrote it. But wait, I didn't actually implement the key wait logic fully robustly.
        # Let's fix DataAcquisition or just implement the loop here.
        # Actually, let's just use record_sample directly here to be safer.
        
        samples_target = 8
        current_samples = len(list((Path("dataset") / term).glob("*.mp4")))
        
        while current_samples < samples_target:
            input(f"Ready to record sample {current_samples+1}/{samples_target} for '{term}'. Press ENTER to record.")
            recorder.record_sample(term)
            current_samples += 1
            print(f"Saved. Total: {current_samples}")
            
    print("Collection run complete.")

if __name__ == "__main__":
    main()
