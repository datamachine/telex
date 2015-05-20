import logging
try:
    import tgl
except ImportError:
    import test_harness.tgl as tgl

from configobj import ConfigObj
import re
from TelegramPluginManager import TelegramPluginManager

#logging.basicConfig(level=logging.DEBUG)



class TelegramBot:
    our_id = 0
    binlog_done = False

    def __init__(self):
        self.config = ConfigObj("telegram-bot.conf")
        if len(self.config) == 0:
            self.init_config()

        try:
            self.admins = int(self.config["admin_users"])
        except:
            self.admins = [int(admin) for admin in self.config["admin_users"]]

        self.plugin_manager = TelegramPluginManager(self)
        self.plugin_manager.collectPlugins()


    # Config Management
    def init_config(self):
        self.config["admin_users"] = [
            self.our_id,
        ]

        self.config.write()

    # Util
    def admin_check(self, msg):
        if msg["from"]["id"] == self.admins or msg["from"]["id"] in self.admins:
            return True
        else:
            ptype, pid = self.get_peer_to_send(msg)
            tgl.send_msg(ptype, pid, "Admin required for this feature")
            return False

    def get_peer_to_send(self, msg):
        if msg.dest.id == self.our_id:  # direct message
            peer = msg.src
        else:  # chat room
            peer = msg.dest

        return peer

    def download_to_file(self, url, ext):
        try:
            import urllib.request
            import tempfile
            filehdl, file_name = tempfile.mkstemp("." + ext)

            urllib.request.urlretrieve(url, file_name)

            return file_name
        except:
            return None

    # Callbacks
    def on_binlog_replay_end(self):
        self.binlog_done = True

    def on_get_difference_end(self):
        pass

    def on_our_id(self, current_id):
        self.our_id = current_id
        return "Set ID: " + str(self.our_id)

    def on_msg_receive(self, msg):
        if msg.out or not self.binlog_done:
            return

        peer = get_peer_to_send(msg)

        # run pre_process
        for plugin_info in self.plugin_manager.getAllPlugins():
            if plugin_info.plugin_object.is_activated:
                plugin_info.plugin_object.pre_process(msg)



        # run matches
        for plugin_info in self.plugin_manager.getAllPlugins():
            for pattern in plugin_info.plugin_object.patterns:
                if plugin_info.plugin_object.is_activated and hasattr(msg, 'text'):
                    matches = re.search(pattern, msg.text)
                    if matches is not None:
                        reply = plugin_info.plugin_object.run(msg, matches)

                        if reply is not None:
                            peer.send_msg(reply)

        tgl.mark_read(peer)

    def on_secret_chat_update(self, peer, types):
        pass

    def on_user_update(self, peer, types):
        pass

    def on_chat_update(self, peer, types):
        pass

