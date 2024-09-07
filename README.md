# Domain-Backup-Finder
A script for finding backup files based on each domain names for .zip,.sql,.tar.gz .

# Example

Input URL: www.example.com

Will Check For These URLs:

* https://www.example.com/example.com.zip
* https://www.example.com/example.zip
* https://www.example.com/example.com.sql
* https://www.example.com/example.sql
* https://www.example.com/example.com.tar.gz
* https://www.example.com/example.tar.gz

## Usage

 $~ usage: python backupfinder.py urls.txt output.txt
