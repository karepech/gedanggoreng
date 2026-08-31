import requests
import time
import os

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_all_sports_m3u():
    query = 'extension:m3u "group-title=" sports OR live'
    base_url = f"https://api.github.com/search/code?q={query}&per_page=30"
    
    playlist_content = ["#EXTM3U\n"]
    seen_urls = set()
    
    # Kumpulan kata kunci untuk mencakup "semua kategori sports"
    sports_keywords = [
        "sport", "football", "soccer", "basketball", "nba", "nfl", 
        "mlb", "tennis", "golf", "f1", "racing", "cricket", "wwe", 
        "ufc", "boxing", "bein", "espn", "sky sports", "eurosport", "liga"
    ]
    
    for page in range(1, 4):
        response = requests.get(f"{base_url}&page={page}", headers=HEADERS)
        if response.status_code != 200:
            break
            
        items = response.json().get('items', [])
        if not items:
            break
            
        for item in items:
            raw_url = item['html_url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
            try:
                m3u_resp = requests.get(raw_url, timeout=10)
                if m3u_resp.status_code == 200:
                    lines = m3u_resp.text.splitlines()
                    
                    for i in range(len(lines)):
                        line = lines[i].strip()
                        if line.startswith("#EXTINF"):
                            # Menggunakan huruf kecil untuk pencarian agar akurat,
                            # tetapi tetap mempertahankan huruf besar/kecil (case) asli pada teks saat disimpan
                            line_lower = line.lower()
                            
                            if i + 1 < len(lines):
                                stream_url = lines[i+1].strip()
                                
                                if stream_url.startswith("http"):
                                    if any(kw in line_lower for kw in sports_keywords):
                                        if stream_url not in seen_urls:
                                            playlist_content.append(line + "\n")
                                            playlist_content.append(stream_url + "\n")
                                            seen_urls.add(stream_url)
            except Exception:
                continue
                
        time.sleep(2)
        
    # NAMA FILE TETAP agar tidak perlu ubah konfigurasi actions (.yml)
    with open("sports_live.m3u", "w", encoding="utf-8") as file:
        file.writelines(playlist_content)

if __name__ == "__main__":
    get_all_sports_m3u()
