from twx import TWXBotApi
from telex import TelexBot
import configparser

config = configparser.ConfigParser()
config.read('telex.conf')

backend = TWXBotApi(token=config['Backend']['token'])
bot = TelexBot(backend)

# Set callbacks
backend.on_msg_receive = bot.on_msg_receive
backend.on_user_update = bot.on_user_update
backend.on_chat_update = bot.on_chat_update

# Start backend main loop
backend.start()

# TODO: Do we still want this to be set via callback?
bot.our_id = backend.bot_id
