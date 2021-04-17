#!/bin/bash

# Run
docker run -d \
--name=harley-bot \
--restart always \
--network postgres \
harley-bot:latest
