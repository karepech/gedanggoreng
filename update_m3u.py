import requests
import time
import os

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_separated_sports_m3u():
    query = 'extension:m3u "group-title=" sports OR live'
    base_url = f"https://api.github.com/search/code?q={query}&per_page=30"
    
    sports_content = ["#EXTM3U\n"]
    live_content = ["#EXTM3U\n"]
    
    seen_sports_urls = set()
    seen_live_urls = set()
    provider_urls = set() # Penampung untuk link penyedia
    
    sports_keywords = [
        "sport", "football", "soccer", "basketball", "nba", "nfl", 
        "mlb", "tennis", "golf", "f1", "racing", "cricket", "wwe", 
        "ufc", "boxing", "bein", "espn", "sky sports", "eurosport", "liga"
    ]
    live_keywords = ["live", "event"]
    
    for page in range(1, 4):
        response = requests.get(f"{base_url}&page={page}", headers=HEADERS)
        if response.status_code != 200:
            break
            
        items = response.json().get('items', [])
        if not items:
            break
            
        for item in items:
            # html_url adalah link tampilan asli GitHub (mudah diklik/dibaca)
            html_url = item['html_url']
            raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
            try:
                m3u_resp = requests.get(raw_url, timeout=10)
                if m3u_resp.status_code == 200:
                    lines = m3u_resp.text.splitlines()
                    
                    has_valid_channel = False # Penanda jika ada channel yang diambil dari file ini
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        if line.startswith("#EXTINF"):
                            current_block = [line]
                            extinf_lower = line.lower()
                            stream_url = ""
                            
                            j = i + 1
                            while j < len(lines):
                                next_line = lines[j].strip()
                                
                                if not next_line:
                                    j += 1
                                    continue
                                    
                                if next_line.startswith("#EXTINF"):
                                    break
                                    
                                current_block.append(next_line)
                                
                                if next_line.startswith("http"):
                                    stream_url = next_line
                                    break
                                    
                                j += 1
                                
                            if stream_url:
                                is_sport = any(kw in extinf_lower for kw in sports_keywords)
                                is_live = any(kw in extinf_lower for kw in live_keywords)
                                
                                if is_sport and stream_url not in seen_sports_urls:
                                    for block_line in current_block:
                                        sports_content.append(block_line + "\n")
                                    seen_sports_urls.add(stream_url)
                                    has_valid_channel = True
                                    
                                if is_live and stream_url not in seen_live_urls:
                                    for block_line in current_block:
                                        live_content.append(block_line + "\n")
                                    seen_live_urls.add(stream_url)
                                    has_valid_channel = True
                                    
                            i = j if stream_url else i + 1
                        else:
                            i += 1
                            
                    # Jika ada setidaknya 1 channel yang diambil, simpan URL penyedianya
                    if has_valid_channel:
                        provider_urls.add(html_url)
                        
            except Exception:
                continue
                
        time.sleep(2)
        
    with open("sports.m3u", "w", encoding="utf-8") as file:
        file.writelines(sports_content)
        
    with open("live_event.m3u", "w", encoding="utf-8") as file:
        file.writelines(live_content)
        
    # Menyimpan daftar link penyedia
    with open("penyedia.txt", "w", encoding="utf-8") as file:
        file.write("Daftar URL Repositori Penyedia M3U:\n")
        file.write("="*40 + "\n")
        for url in sorted(provider_urls):
            file.write(url + "\n")

if __name__ == "__main__":
    get_separated_sports_m3u()
