__author__ = 'impelligent'
import requests
from lxml import html
import argparse
from dotenv import load_dotenv
from os import environ as env
from datetime import datetime

parser = argparse.ArgumentParser()
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


class PfBak:
    
    def __init__(self):
        self.backup_name = f"config-pfSense-{HOST}-{datetime.now().strftime('%m-%d-%Y,%H:%M:%S')}.xml"
        # set ssl verify type
        if args.verify:
            self.verify = True
        else:
            self.verify = False
        print(self.verify)
        # set host
        if args.http:
            self.host = f"http://{HOST}/"
        else:
            self.host = f"https://{HOST}/"
        print(self.host)

        self.session = requests.session()
    
    def backup_config(self):
        self.getCSRF()
        self.login()
        self.getCSRF(exist=True)
        self.getConfig()
        
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
        
        
        if args.verbose:
            print(f'Saving the Configuration to: backups/{self.backup_name}')
        with open(f"backups/{self.backup_name}", "w") as f:
            f.write(r.text)

if __name__ == "__main__":
    backup = PfBak()
    backup.backup_config()