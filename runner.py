import tgl
from TelegramBot import TelegramBot

bot = TelegramBot()

# Set callbacks
tgl.set_on_binlog_replay_end(bot.on_binlog_replay_end)
tgl.set_on_get_difference_end(bot.on_get_difference_end)
tgl.set_on_our_id(bot.on_our_id)
tgl.set_on_msg_receive(bot.on_msg_receive)
tgl.set_on_secret_chat_update(bot.on_secret_chat_update)
tgl.set_on_user_update(bot.on_user_update)
tgl.set_on_chat_update(bot.on_chat_update)
