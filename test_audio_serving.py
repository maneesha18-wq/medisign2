
import requests

def test_audio_serving():
    url = "http://localhost:5000/audio/headache_20260318_010916_765.mp3"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
    except Exception as e:
        print(f"Error: {e}")
    print(dict(response.headers))

if __name__ == "__main__":
    test_audio_serving()
