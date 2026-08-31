import requests
import time
import os

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_filtered_m3u():
    # Kueri mencari file m3u yang kemungkinan memiliki kategori grup
    query = 'extension:m3u "group-title=" sports OR live'
    base_url = f"https://api.github.com/search/code?q={query}&per_page=30"
    
    playlist_content = ["#EXTM3U\n"]
    keywords = ["sport", "live event", "live"]
    seen_urls = set() # Mencegah link duplikat
    
    for page in range(1, 4): # Mengambil maksimal 90 file agar aksi tidak timeout
        response = requests.get(f"{base_url}&page={page}", headers=HEADERS)
        if response.status_code != 200:
            break
            
        items = response.json().get('items', [])
        if not items:
            break
            
        for item in items:
            raw_url = item['html_url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
            try:
                # Mengunduh isi file m3u secara langsung
                m3u_resp = requests.get(raw_url, timeout=10)
                if m3u_resp.status_code == 200:
                    lines = m3u_resp.text.splitlines()
                    
                    for i in range(len(lines)):
                        line = lines[i].strip()
                        if line.startswith("#EXTINF"):
                            line_lower = line.lower()
                            
                            # Cek apakah baris metadata mengandung kata kunci target
                            if any(kw in line_lower for kw in keywords):
                                if i + 1 < len(lines):
                                    stream_url = lines[i+1].strip()
                                    # Pastikan baris bawahnya adalah link dan belum pernah dimasukkan
                                    if stream_url.startswith("http") and stream_url not in seen_urls:
                                        playlist_content.append(line + "\n")
                                        playlist_content.append(stream_url + "\n")
                                        seen_urls.add(stream_url)
            except Exception:
                continue
                
        time.sleep(2) # Jeda API rate limit
        
    with open("sports_live.m3u", "w", encoding="utf-8") as file:
        file.writelines(playlist_content)

if __name__ == "__main__":
    get_filtered_m3u()
