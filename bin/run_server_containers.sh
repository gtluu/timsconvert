#!/bin/bash

docker run --rm timsconvert_server
docker run --rm timsconvert_worker
docker run --rm redis
docker run --rm rq_dashboard
