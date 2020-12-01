import os
import json
import cloudscraper
from bs4 import BeautifulSoup

class WarcraftAddonManager(object):
    def __init__(self, addon_path, config_file):
        # if not os.path.exists(addon_path):
        #     raise FileNotFoundError
        # if not os.path.exists(config_file):
        #     self.config = {}
        #     with open(config_file, 'w') as f:
        #         json.dump(self.config, f)
        # else:
        #     with open(config_file, 'r') as f:
        #         self.config = json.load(f)
                
        self.addon_path = addon_path
        
        
    def add_new_addon(self, addon_link):
        scraper = cloudscraper.create_scraper()
        r = scraper.get(addon_link)
        soup = BeautifulSoup(r.text, features='html.parser')
        addon_name = soup.find("meta",  property="og:title")["content"]
        last_update = soup.find('abbr')['title']
        download_page = scraper.get(f'{addon_link}/download')
        download_soup = BeautifulSoup(download_page.text, features='html.parser')
        link = download_soup.find('p', {'class':'text-sm'}).find('a')['href']
        download_link = f'http://www.curseforge.com{link}'

        files = scraper.get(download_link)
        with open(os.path.join(self.addon_path, 'addon.zip'), 'wb') as f:
            f.write(files.content)