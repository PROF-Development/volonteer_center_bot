from os import getenv
import dotenv


dotenv.load_dotenv()

BOT_TOKEN = getenv("TOKEN")
SKIP_UPDATES = bool(getenv("SKIP_UPDATES"))

assert type(BOT_TOKEN) is str
assert type(SKIP_UPDATES) is bool
