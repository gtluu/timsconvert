#!/bin/bash

docker run --rm -it --detach timsconvert_server
docker run --rm -it --name timsconvert_redis --detach redis
docker run --rm -it --detach timsconvert_worker
docker run --rm -it --detach rq_dashboard
