# pfBak

pfSense Backup Automation for extracting config via pfSense Web Interface.

***Tested on pfSense 2.52*** 

# Requirements
- Python 3.10
- lxml
- requests
- load_dotenv

# Usage
```
usage: pfBak.py [-h] [-v] [-i] [-verify]

options:
  -h,      --help         show this help message and exit
  -v,      --verbose      increase output verbosity
  -i,      --http         Use http instead of https
  -verify, --verify       Verify SSL

```

# Example

If you haven't already, install pip and virtualenv :

```
sudo apt-get install python3-pip
sudo pip3 install virtualenv
```

#### Then run the bootstrap script
- `bootstrap_env.sh`

#### Then source your environment
- `source venv/bin/activate`

#### Trigger Backup
- `python pfBak.py -ve -v` 


