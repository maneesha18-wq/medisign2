
import requests
import os

def test_api():
    url = "http://localhost:5000/api/recognize"
    # Find a sample video from the dataset/raw_videos to test
    sample_dir = r"c:\Users\vishn\OneDrive\Desktop\New folder\medisign\dataset\raw_videos\fever"
    if not os.path.exists(sample_dir):
        print("Sample dir not found")
        return
    
    videos = [v for v in os.listdir(sample_dir) if v.endswith(".mp4")]
    if not videos:
        print("No videos found")
        return
    
    video_path = os.path.join(sample_dir, videos[0])
    print(f"Testing with: {video_path}")
    
    with open(video_path, 'rb') as f:
        files = {'video': f}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
