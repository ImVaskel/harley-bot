# Harley Bot

## Info
To run this bot you must have a postgresql Docker container on a network called `postgres` (look into tutorials on this).

Then fill out the config with the proper info and move it to a file called `config.json`.

## Run

To run the bot, first build the image with the `build.sh` script. Then run `run.sh` to run the container. 

The docker container runs on `buster-slim` on `python 3.9`. Note that some of the bot is hard coded, so you may have to change some of it.

# **NOTE** 
This bot is unfinished, and chances are it'll stay that way. Open a PR if you want anything finished and I'll look at it.

## **Licensing**
The bot is under an AGPL-3 license. So please follow that.