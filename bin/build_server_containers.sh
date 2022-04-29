#!/bin/bash

docker build --tag timsconvert_server -f Dockerfile.server .
docker build --tag timsconvert_worker -f Dockerfile.worker .
docker pull redis
wget -O Dockerfile.rqdashboard https://raw.githubusercontent.com/Parallels/rq-dashboard/master/Dockerfile
docker build --tag rq_dashboard -f Dockerfile.rqdashboard .
rm Dockerfile.rqdashboard
