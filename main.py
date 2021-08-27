from utils.subclasses import HarleyBot
import logging
import coloredlogs

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

coloredlogs.install(fmt="%(asctime)s | %(name)s | %(levelname)s > %(message)s")

if __name__ == "__main__":

    bot = HarleyBot()

    bot.run()
