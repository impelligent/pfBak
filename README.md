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
`python3 pfBak.py -ve -v` 