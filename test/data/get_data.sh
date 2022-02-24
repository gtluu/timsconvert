#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

wget -r -l=0 -P "$parent_path" --ftp-user=MSV000088438 --ftp-password=a ftp://massive.ucsd.edu
wget -r -l=0 -P "$parent_path" --ftp-user=MSV000084402 --ftp-password=a ftp://massive.ucsd.edu
