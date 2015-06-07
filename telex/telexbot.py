import tgl

import re
from .TelexPluginManager import TelexPluginManager


class TelexBot:
    our_id = 0
    binlog_done = False

    def __init__(self):
        self.plugin_manager = TelexPluginManager(self)
        self.plugin_manager.collectPlugins()

    # Util
    def admin_check(self, msg):
        if msg.src.id == self.admins or msg.src.id in self.admins:
            return True
        else:
            peer = self.get_peer_to_send(msg)
            peer.send_msg("Admin required for this feature")
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
    def on_loop(self):
        pass

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

        peer = self.get_peer_to_send(msg)

        # run pre_process
        for plugin_info in self.plugin_manager.getAllPlugins():
            if plugin_info.plugin_object.is_activated:
                plugin_info.plugin_object.pre_process(msg)



        # run matches
        for plugin_info in self.plugin_manager.getAllPlugins():
            if not hasattr(plugin_info.plugin_object, 'patterns'):
                print('ERROR: plugin "{}" does not has required "patterns" list/dict'.format(plugin_info.name))
                continue
            if type(plugin_info.plugin_object.patterns) is dict:
                for pattern, func in plugin_info.plugin_object.patterns.items():
                    if plugin_info.plugin_object.is_activated and msg.text is not None:
                        matches = re.search(pattern, msg.text)
                        if matches is not None:
                            if type(func) is str:
                                func = getattr(plugin_info.plugin_object, func)
                            if not func:
                                func = plugin_info.plugin_object.run
                            reply = func(msg, matches)
                            if reply is not None:
                                peer.send_msg(reply)
            elif  type(plugin_info.plugin_object.patterns) is list:
                for pattern in plugin_info.plugin_object.patterns:
                    if plugin_info.plugin_object.is_activated and msg.text is not None:
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

