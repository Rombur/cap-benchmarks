#! /bin/bash

docker run --net=host -v /home/bt2/Documents/cap-benchmarks:/scratch dalg24/cap-stack /scratch/benchmark.sh
docker rm $(docker ps -a -q)
