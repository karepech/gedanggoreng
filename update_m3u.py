import requests
import time
import os

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_filtered_m3u():
    # Kueri mencari file m3u yang relevan
    query = 'extension:m3u "group-title=" sports OR live'
    base_url = f"https://api.github.com/search/code?q={query}&per_page=30"
    
    # Menyiapkan dua penampung berbeda
    sports_content = ["#EXTM3U\n"]
    live_content = ["#EXTM3U\n"]
    
    # Filter duplikat terpisah untuk masing-masing file
    seen_sports_urls = set()
    seen_live_urls = set()
    
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
                            line_lower = line.lower()
                            
                            if i + 1 < len(lines):
                                stream_url = lines[i+1].strip()
                                
                                # Pastikan itu adalah URL yang valid
                                if stream_url.startswith("http"):
                                    
                                    # Deteksi Kategori
                                    is_sport = "sport" in line_lower
                                    is_live = "live" in line_lower or "event" in line_lower
                                    
                                    # Memasukkan ke file Sports
                                    if is_sport and stream_url not in seen_sports_urls:
                                        sports_content.append(line + "\n")
                                        sports_content.append(stream_url + "\n")
                                        seen_sports_urls.add(stream_url)
                                        
                                    # Memasukkan ke file Live Event
                                    if is_live and stream_url not in seen_live_urls:
                                        live_content.append(line + "\n")
                                        live_content.append(stream_url + "\n")
                                        seen_live_urls.add(stream_url)
            except Exception:
                continue
                
        time.sleep(2)
        
    # Menyimpan file pertama (Sports)
    with open("sports.m3u", "w", encoding="utf-8") as file:
        file.writelines(sports_content)
        
    # Menyimpan file kedua (Live Events)
    with open("live_event.m3u", "w", encoding="utf-8") as file:
        file.writelines(live_content)

if __name__ == "__main__":
    get_filtered_m3u()
