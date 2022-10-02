__author__ = 'impelligent'
import requests
from lxml import html
from argparse import ArgumentParser
from dotenv import load_dotenv
from os import environ as env, path, makedirs, stat, listdir, remove
from time import time
from datetime import datetime

parser = ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
parser.add_argument("-i", "--http", action="store_true", help="use http instead of https")
parser.add_argument("-verify", "--verify", action="store_true", help="Verify SSL")
args = parser.parse_args()

load_dotenv()
HOST = env.get('HOST')
USERNAME = env.get('USERNAME')
PASSWORD = env.get('PASSWORD')
ENCRYPTED_PASS = env.get('ENCRYPTED_PASS')
BACKUP_RRD = env.get('BACKUP_RRD')
BACKUP_PKG = env.get('BACKUP_PKG')
BACKUP_DATA = env.get('BACKUP_DATA')
DAYS_OF_BACKUPS = env.get('DAYS_OF_BACKUPS', 7)
BACKUP_DIR = env.get('BACKUP_DIR', 'backups')


class PfBak:
    
    def __init__(self):
        self.days = 60 * 60 * 24 * int(DAYS_OF_BACKUPS if DAYS_OF_BACKUPS else 7)
        self.backup_name = f"config-pfSense-{HOST}-{datetime.now().strftime('%m-%d-%Y,%H:%M:%S')}.xml"
        self.backup_dir = BACKUP_DIR if BACKUP_DIR else 'backups'
        # set ssl verify type
        if args.verify:
            self.verify = True
        else:
            self.verify = False
        
        # set host
        if args.http:
            self.host = f"http://{HOST}/"
        else:
            self.host = f"https://{HOST}/"
        
        if not path.exists(self.backup_dir):
            makedirs(self.backup_dir)
            
        self.session = requests.session()
    
    def executeProcess(self):
        self.getCSRF()
        self.login()
        self.getCSRF(exist=True)
        self.getConfig()
        self.deleteOldConfigs()
        
    def getCSRF(self, exist=False):

        # Get the Magic CSRF Token
        if not exist:
            if args.verbose:
                print('retrieving the "magic" CSRF Token.')
            
            r = self.session.get(f"{self.host}index.php",
                                 verify=self.verify)
            try:
                self.magic_csrf_token = html.fromstring(r.text).xpath('//input[@name=\'__csrf_magic\']/@value')[0]
            except:
                self.magic_csrf_token = ""
            if args.verbose:
                print(f'Token: {self.magic_csrf_token}')
        else:
            # get new csrf token
            self.magic_csrf_token = html.fromstring(self.resp.text).xpath('//input[@name=\'__csrf_magic\']/@value')[0]
            if html.fromstring(self.resp.text).xpath('//title/text()')[0].startswith("Login"):
                exit("Login was not Successful!")
            
    def login(self):
        # Login into Firewall Webinterface
        if args.verbose:
            print(f'Logging in, into {self.host}')
        self.resp = self.session.post(f"{self.host}index.php",
                   data={
                       "__csrf_magic": self.magic_csrf_token,
                       "usernamefld": USERNAME,
                       "passwordfld": PASSWORD,
                        "login": "Login"
                   },
                   verify=self.verify)
    def getConfig(self):
        # download configuration
        if args.verbose:
            print('retrieving the Configuration File')
            print(self.magic_csrf_token)
            
        data = {
            "__csrf_magic": self.magic_csrf_token,
            "download": "Download configuration as XML",
        }
        if ENCRYPTED_PASS:
            data["encrypt"] = "yes"
            data["encrypt_password"] = ENCRYPTED_PASS
            data["encrypt_password_confirm"] = ENCRYPTED_PASS
        
        if not BACKUP_RRD:
            data['donotbackuprrd'] = "yes"
        
        if not BACKUP_PKG:
            data['nopackages'] = "yes"
        
        if BACKUP_DATA:
            data["backupdata"] = "yes"
            
        r = self.session.post(f"{self.host}diag_backup.php",
                              data=data,
                              verify=self.verify)
        
        if not ENCRYPTED_PASS:
            if html.fromstring(r.text).xpath('count(//pfsense)') != 1.0:
                exit("Something went wrong! the returned Content was not a PfSense Configuration File!")
        
        else:
            if not 'config.xml' in str(r.text):
                exit("Something went wrong! the returned Content was not a PfSense Configuration File!")
        
        if args.verbose:
            print(f'Saving the Configuration to: {self.backup_dir}/{self.backup_name}')
            
        with open(f"{self.backup_dir}/{self.backup_name}", "w") as f:
            f.write(r.text)
        if args.verbose:
            print(f'Configuration saved.')

    def deleteOldConfigs(self):
        if args.verbose:
            print(f'Deleting Configs older than {DAYS_OF_BACKUPS} days.')
            
        for filename in listdir(self.backup_dir):
            filestamp = stat(path.join(self.backup_dir, filename)).st_mtime
            if filestamp < time() - self.days:
                if args.verbose:
                    print(f'Deleting Config : {self.backup_dir}/{filename}')
                remove(f'{self.backup_dir}/{filename}')

if __name__ == "__main__":
    backup = PfBak()
    backup.executeProcess()