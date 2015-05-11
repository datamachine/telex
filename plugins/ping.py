import TelegramBot
import plugintypes
import tgl


class PingPlugin(plugintypes.TelegramPlugin):
    def setup(self):
        pass

    def teardown(self):
        pass

    def on_msg_receive(self, msg):
        if msg["out"] and not self.bot.binlog_done:
            return

        if msg["to"]["id"] == self.bot.our_id:  # direct message
            ptype = msg["from"]["type"]
            pid = msg["from"]["id"]
        else:  # chat room
            ptype = msg["to"]["type"]
            pid = msg["to"]["id"]

        text = msg["text"]

        if text.startswith("!ping"):
            print("SENDING PONG")
            TelegramBot.send_msg(ptype, pid, "PONG!")