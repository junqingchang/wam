import os
import json
import cloudscraper
from bs4 import BeautifulSoup
from zipfile import ZipFile

class WarcraftAddonManager(object):
    def __init__(self, config_file):
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            addon_path = self.request_user_addon_path()
            if not os.path.exists(addon_path):
                raise FileNotFoundError
            self.config = {'addon_path': addon_path, 'addons': {}}
            self.save_config()

        with open(config_file, 'r') as f:
            self.config = json.load(f)
            addon_path = self.config['addon_path']
                
        self.addon_path = addon_path
        
    def add_new_addon(self, addon_link):
        #TODO Error check for html errors
        scraper = cloudscraper.create_scraper()
        r = scraper.get(addon_link)
        soup = BeautifulSoup(r.text, features='html.parser')
        addon_name = soup.find("meta",  property="og:title")["content"]
        last_update = soup.find('abbr')['title']
        converted_time = self.convert_datetime(last_update.split()[:4])

        download_page = scraper.get(f'{addon_link}/download')
        download_soup = BeautifulSoup(download_page.text, features='html.parser')
        link = download_soup.find('p', {'class':'text-sm'}).find('a')['href']
        download_link = f'http://www.curseforge.com{link}'

        files = scraper.get(download_link)

        existing_addons = os.listdir(self.addon_path)

        with open(os.path.join(self.addon_path, 'addon.zip'), 'wb') as f:
            f.write(files.content)

        with ZipFile(os.path.join(self.addon_path, 'addon.zip'), 'r') as zipobj:
            zipobj.extractall(self.addon_path)

        os.remove(os.path.join(self.addon_path, 'addon.zip'))

        all_addons = os.listdir(self.addon_path)
        new_files = [x for x in all_addons if x not in existing_addons]

        if addon_name in self.config['addons']:
            overwrite = self.warn_user_duplicate_addon()
            if not overwrite:
                return

        self.config['addons'][addon_name] = {'link': addon_link, 'last_update': converted_time, 'files': new_files}
        self.save_config()

    def request_user_addon_path(self):
        return input('Full Addon Path?\n')

    def convert_datetime(self, datetime):
        m, d, y, t = datetime
        m = int(m)*30*24*60*60
        d = int(d)*24*60*60
        y = int(y)*365*30*24*60*60
        t = [int(x) for x in t.split(':')]
        t = t[0]*60*60 + t[1]*60 + t[2]
        return m+d+y+t

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def warn_user_duplicate_addon(self):
        print('Duplicate Addon Detected. Overwrite? (y/n)')
        while True:
            overwrite_command = input()
            if overwrite_command == 'y':
                return True
            elif overwrite_command == 'n':
                return False
            else:
                print('Invalid command. Type y for overwrite, n to keep existing')

    def update_addon(self, addon_name):
        addon_link = self.config['addons'][addon_name]['link']
        addon_last_update = self.config['addons'][addon_name]['last_update']

        scraper = cloudscraper.create_scraper()
        r = scraper.get(addon_link)
        soup = BeautifulSoup(r.text, features='html.parser')
        addon_name = soup.find("meta",  property="og:title")["content"]
        last_update = soup.find('abbr')['title']
        converted_time = self.convert_datetime(last_update.split()[:4])

        if converted_time > addon_last_update:
            self.remove_addon(addon_name)
            download_page = scraper.get(f'{addon_link}/download')
            download_soup = BeautifulSoup(download_page.text, features='html.parser')
            link = download_soup.find('p', {'class':'text-sm'}).find('a')['href']
            download_link = f'http://www.curseforge.com{link}'

            files = scraper.get(download_link)
            existing_addons = os.listdir(self.addon_path)
            with open(os.path.join(self.addon_path, 'addon.zip'), 'wb') as f:
                f.write(files.content)

            with ZipFile(os.path.join(self.addon_path, 'addon.zip'), 'r') as zipobj:
                zipobj.extractall(self.addon_path)

            os.remove(os.path.join(self.addon_path, 'addon.zip'))

            all_addons = os.listdir(self.addon_path)
            new_files = [x for x in all_addons if x not in existing_addons]

            self.config['addons'][addon_name]['last_update'] = converted_time
            self.config['addons'][addon_name]['files'] = new_files
            self.save_config()

    def update_all_addons(self):
        for addon in self.config['addons']:
            self.update_addon(addon)

    def remove_addon(self, addon_name):
        addon_files = self.config['addons'][addon_name]['files']
        for folder in addon_files:
            os.rmdir(folder)
        del self.config['addons'][addon_name]
        self.save_config()

    def wam_cmd(self):
        while True:
            print('World of Warcraft Addon Manager')
            print('1: Add New Addon')
            print('2: Remove Addon')
            print('3: Update Specific Addon')
            print('4: Update All Addon')
            print('5: Add/Update Elvui')
            print('6: Remove Elvui')
            print('q: Quit')
            user_cmd = input()

            if user_cmd == 'q':
                break
            elif user_cmd == '1':
                addon_link = input('Please enter addon link to add\n')
                self.add_new_addon(addon_link=addon_link)
                print('Addon added, returning to main menu')
            elif user_cmd == '2':
                addon_name = input('Please enter addon name to delete\n')
                self.remove_addon(addon_name=addon_name)
                print('Addon removed, returning to main menu')
            elif user_cmd == '3':
                addon_name = input('Please enter addon name to update\n')
                self.update_addon(addon_name)
                print('Addon updated, returning to main menu')
            elif user_cmd == '4':
                print('Updating all addons')
                self.update_all_addons()
                print('Addons updated, returning to main menu')
            elif user_cmd == '5':
                print('Adding/Updating Elvui')
                self.add_update_elvui()
                print('Elvui Installed/Updated, returning to main menu')
            elif user_cmd == '6':
                print('Removing Elvui')
                self.remove_elvui()
                print('Elvui removed, returning to main menu')
            else:
                print('Invalid Command. Please Enter a Valid Command')

    def add_update_elvui(self):
        scraper = cloudscraper.create_scraper()
        r = scraper.get('https://www.tukui.org/download.php?ui=elvui')
        soup = BeautifulSoup(r.text, features='html.parser')
        link_ext = soup.find('div', {'class':'mb-10'}).find('a')['href']
        download_link = f'https://www.tukui.org{link_ext}'
        files = scraper.get(download_link)
        existing_addons = os.listdir(self.addon_path)
        with open(os.path.join(self.addon_path, 'elvui.zip'), 'wb') as f:
            f.write(files.content)

        with ZipFile(os.path.join(self.addon_path, 'elvui.zip'), 'r') as zipobj:
            zipobj.extractall(self.addon_path)

        os.remove(os.path.join(self.addon_path, 'elvui.zip'))
        all_addons = os.listdir(self.addon_path)
        new_files = [x for x in all_addons if x not in existing_addons]
        print(new_files)
        if 'elvui' not in self.config:
            self.config['elvui'] = {'files': []}
        self.config['elvui']['files'] += new_files
        self.save_config()

    def remove_elvui(self):
        addon_files = self.config['elvui']['files']
        for folder in addon_files:
            os.rmdir(folder)
        del self.config['elvui']
        self.save_config()