import json
import threading
import sys

import requests

def main():
    weather_urls = [
        "http://www.tianqihoubao.com/lishi/jiaxing/month/{}{}.html".format(
            year, str(month) if len(str(month)) == 2 else "0{}".format(month)
        )
        for month in range(1, 13) for year in range(2014, 2023)
    ]
    
    aqi_urls = [
        "http://tianqihoubao.com/aqi/jiaxing-{}{}.html".format(
            year, str(month) if len(str(month)) == 2 else "0{}".format(month)
        )
        for month in range(1, 13) for year in range(2014, 2023)
    ]
    
    urls = [*weather_urls, *aqi_urls]
    
    data = {}
    
    def add(url):
        while True:
            try:
                d = requests.get(url, headers = {
                    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                }, timeout=10).text
            except:
                print(f"{url} Failed... Retrying...")
            else:
                print(f"{url} Done")
                data[url]=d
                break
    
    for url in urls:
        print(f"Getting {url}")
        thread = threading.Thread(target=add, args=(url,), name=url)
        thread.daemon = True
        thread.start()
    
    while len(data) != len(urls):
        for url in urls:
            if url not in data.keys():
                print(url)
        print(len(data), "Done")
        c = input()
        if c == "save":
            with open("result.json", "w+") as fb:
                fb.write(json.dumps(data))
            sys.exit(0)
    with open("result.json", "w+") as fb:
        fb.write(json.dumps(data))
    
if __name__ == "__main__":
    main()