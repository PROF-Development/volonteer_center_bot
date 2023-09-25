from bot.src.misc import executor
import bot.src.handlers
import sys

sys.stderr = open('log_errors.txt', 'w')

if __name__ == "__main__":
    executor.start_polling()
