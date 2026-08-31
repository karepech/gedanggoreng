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
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        if line.startswith("#EXTINF"):
                            # Menyiapkan penampung untuk satu blok penuh
                            current_block = [line]
                            extinf_lower = line.lower()
                            stream_url = ""
                            
                            # Terus periksa baris di bawahnya sampai menemukan link http
                            j = i + 1
                            while j < len(lines):
                                next_line = lines[j].strip()
                                
                                # Lewati jika ada baris kosong
                                if not next_line:
                                    j += 1
                                    continue
                                    
                                # Jika ketemu #EXTINF lagi sebelum link, berarti blok sebelumnya rusak/terpotong
                                if next_line.startswith("#EXTINF"):
                                    break
                                    
                                current_block.append(next_line)
                                
                                # Jika baris adalah link streaming, hentikan pencarian blok
                                if next_line.startswith("http"):
                                    stream_url = next_line
                                    break
                                    
                                j += 1
                                
                            # Jika blok memiliki link streaming yang valid
                            if stream_url:
                                if any(kw in extinf_lower for kw in sports_keywords):
                                    if stream_url not in seen_urls:
                                        # Masukkan seluruh isi blok (tanpa merubah format/huruf asli)
                                        for block_line in current_block:
                                            playlist_content.append(block_line + "\n")
                                        seen_urls.add(stream_url)
                                        
                            # Lompat ke indeks terakhir blok yang baru saja dicek
                            i = j if stream_url else i + 1
                        else:
                            i += 1
            except Exception:
                continue
                
        time.sleep(2)
        
    with open("sports_live.m3u", "w", encoding="utf-8") as file:
        file.writelines(playlist_content)

if __name__ == "__main__":
    get_all_sports_m3u()
