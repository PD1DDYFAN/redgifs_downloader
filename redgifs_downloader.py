import os
import requests

def download_all_videos_from_profile(username, output_folder='downloads', quality='hd'):
    """
    Downloads all videos from a RedGifs user profile using requests.
    
    Args:
    - username (str): The RedGifs username (e.g., 'exampleuser').
    - output_folder (str): Folder to save videos (created if it doesn't exist).
    - quality (str): 'hd' or 'sd' for video quality.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Create a session to persist headers/cookies across requests (required for signatures)
    sess = requests.Session()
    sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    
    # Get temporary guest token (no credentials needed)
    resp = sess.get('https://api.redgifs.com/v2/auth/temporary')
    resp.raise_for_status()
    token = resp.json()['token']
    sess.headers.update({'Authorization': f'Bearer {token}'})
    
    page = 1
    total_downloaded = 0
    
    while True:
        # Fetch page of user content
        params = {
            'page': page,
            'count': 100,  # Max per page; adjust lower if rate-limited
            'order': 'new'
        }
        resp = sess.get(f'https://api.redgifs.com/v2/users/{username.lower()}/search', params=params)
        if resp.status_code == 404:
            raise ValueError(f"User '{username}' not found. Please check the username.")
        resp.raise_for_status()
        data = resp.json()
        
        gifs = data.get('gifs', [])
        if not gifs:
            break  # No more content
        
        for gif in gifs:
            # Select HD or SD URL (already signed by the API)
            video_url = gif['urls'][quality]
            filename = f"{gif['id']}.mp4"
            file_path = os.path.join(output_folder, filename)
            
            # Download using the same session to validate signature
            with sess.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"Downloaded: {filename} ({quality.upper()})")
            total_downloaded += 1
        
        # Check for end of pagination
        if 'pages' in data and page >= data['pages']:
            break
        page += 1
    
    print(f"Total videos downloaded: {total_downloaded}")

# Example usage
if __name__ == "__main__":
    username = input("Enter RedGifs username: ").strip()
    download_all_videos_from_profile(username, output_folder='redgifs_videos', quality='hd')