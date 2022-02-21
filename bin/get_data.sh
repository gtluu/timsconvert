#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

sudo mkdir data
wget -r -P data --ftp-user=MSV000088438 --ftp-password=a ftp://massive.ucsd.edu
