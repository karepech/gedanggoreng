import requests
import time
import os

# Mengambil token dari secret GitHub Actions
TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_raw_m3u_urls():
    query = "extension:m3u"
    base_url = f"https://api.github.com/search/code?q={query}&per_page=100"
    raw_urls = []
    
    for page in range(1, 6): # Mengambil 5 halaman (500 file) untuk efisiensi
        response = requests.get(f"{base_url}&page={page}", headers=HEADERS)
        if response.status_code != 200:
            break
            
        items = response.json().get('items', [])
        if not items:
            break
            
        for item in items:
            raw_url = item['html_url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            raw_urls.append(raw_url)
            
        time.sleep(2)
        
    return raw_urls

if __name__ == "__main__":
    urls = get_raw_m3u_urls()
    # Menyimpan atau menimpa file setiap kali skrip berjalan
    with open("daily_m3u.txt", "w", encoding="utf-8") as file:
        for url in urls:
            file.write(url + "\n")
