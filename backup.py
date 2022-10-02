__author__ = 'impelligent'
import requests
from lxml import html
import argparse
from dotenv import load_dotenv
from os import environ as env

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


if args.verify:
    verify = True
else:
    verify = False
print(verify)
if args.http:
    host = f"http://{HOST}/"
else:
    host = f"https://{HOST}/"
print(host)


s = requests.session()

# Get the Magic CSRF Token
if args.verbose:
    print('retrieving the "magic" CSRF Token.')
    
r = s.get(f"{host}index.php", verify=verify)
try:
    magic_csrf_token = html.fromstring(r.text).xpath('//input[@name=\'__csrf_magic\']/@value')[0]
except:
    magic_csrf_token = ""
if args.verbose:
    print(f'Token: {magic_csrf_token}')
print("test")
# Login into Firewall Webinterface
if args.verbose:
    print(f'Logging in, into {host}')
r = s.post(f"{host}index.php",
           data={
               "__csrf_magic": magic_csrf_token,
               "usernamefld": USERNAME,
               "passwordfld": PASSWORD,
                "login": "Login"
           },
           verify=verify)

#get new csrf token
magic_csrf_token = html.fromstring(r.text).xpath('//input[@name=\'__csrf_magic\']/@value')[0]
if html.fromstring(r.text).xpath('//title/text()')[0].startswith("Login"):
    exit("Login was not Successful!")

# download configuration
if args.verbose:
    print('retrieving the Configuration File')
    print(magic_csrf_token)
    
data = {
    "__csrf_magic": magic_csrf_token,
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
    
r = s.post(f"{host}diag_backup.php",
           data=data,verify=verify)
print(data)
#print(r.text)
if not ENCRYPTED_PASS:
    if html.fromstring(r.text).xpath('count(//pfsense)') != 1.0:
        exit("Something went wrong! the returned Content was not a PfSense Configuration File!")


if args.verbose:
    print('Safing the Configuration to: backup.xml')
with open("backup.xml", "w") as f:
    f.write(r.text)

