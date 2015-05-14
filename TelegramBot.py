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


        self.plugin_manager = TelegramPluginManager(self)
        self.load_plugins()


    # Config Management
    def init_config(self):
        self.config["enabled_plugins"] = [
            "Help",
            "Plugins",
            "Calculator",
            "BTC",
            "Echo",
            "ChatLog",
        ]

        self.config["admin_users"] = [
            self.our_id,
        ]

        self.config.write()

    # Plugin Management
    def load_plugins(self):
        # Tell it the default place(s) where to find plugins
        self.plugin_manager.setPluginPlaces(["./plugins/"])
        # Load all plugins
        self.plugin_manager.collectPlugins()

        # Activate all loaded plugins
        for plugin_info in self.plugin_manager.getAllPlugins():
            plugin_info.bot = self
            if plugin_info.name in self.config["enabled_plugins"]:
                self.plugin_manager.activatePluginByName(plugin_info.name)
            else:
                self.plugin_manager.deactivatePluginByName(plugin_info.name)

    def get_plugins(self):
        return self.plugin_manager.getAllPlugins()

    def get_plugin(self, name):
        return self.plugin_manager.getPluginByName(name)

    def enable_plugin(self, name):
        plugin = self.plugin_manager.activatePluginByName(name)
        if plugin is None:
            return "Plugin {0} does not exist".format(name)
        else:
            self.config["enabled_plugins"].append(name)
            self.config.write()
            return "Plugin {0} enabled".format(name)

    def disable_plugin(self, name):
        plugin = self.plugin_manager.deactivatePluginByName(name)
        if plugin is None:
            return "Plugin {0} does not exist".format(name)
        else:
            try:
                self.config["enabled_plugins"].remove(name)
            except ValueError:
                pass  # Wasn't in the config file.
            self.config.write()
            return "Plugin {0} disabled".format(name)

    # Callbacks
    def on_binlog_replay_end(self):
        self.binlog_done = True

    def on_get_difference_end(self):
        pass

    def on_our_id(self, current_id):
        self.our_id = current_id
        return "Set ID: " + str(self.our_id)

    def on_msg_receive(self, msg):
        if msg["out"] and not self.binlog_done:
            return

        if msg["to"]["id"] == self.our_id:  # direct message
            ptype = msg["from"]["type"]
            pid = msg["from"]["id"]
        else:  # chat room
            ptype = msg["to"]["type"]
            pid = msg["to"]["id"]

        # run pre_process
        for plugin_info in self.plugin_manager.getAllPlugins():
            if plugin_info.plugin_object.is_activated:
                msg = plugin_info.plugin_object.pre_process(msg)



        # run matches
        for plugin_info in self.plugin_manager.getAllPlugins():
            for pattern in plugin_info.plugin_object.patterns:
                if plugin_info.plugin_object.is_activated:
                    matches = re.search(pattern, msg["text"])
                    if matches is not None:
                        reply = plugin_info.plugin_object.run(msg, matches)

                        if reply is not None:
                            send_msg(ptype, pid, reply)

        tgl.mark_read(ptype, pid)

    def on_secret_chat_update(self, peer, types):
        pass

    def on_user_update(self):
        pass

    def on_chat_update(self):
        pass


def send_msg(ptype, pid, msg):
    tgl.send_msg(ptype, pid, msg)

# test driver without tg running
if __name__ == "__main__":
    bot = TelegramBot()

    # Set callbacks
    tgl.set_on_binlog_replay_end(bot.on_binlog_replay_end)
    tgl.set_on_get_difference_end(bot.on_get_difference_end)
    tgl.set_on_our_id(bot.on_our_id)
    tgl.set_on_msg_receive(bot.on_msg_receive)
    tgl.set_on_secret_chat_update(bot.on_secret_chat_update)
    tgl.set_on_user_update(bot.on_user_update)
    tgl.set_on_chat_update(bot.on_chat_update)

    bot.on_binlog_replay_end()
    bot.on_our_id(999)

    import datetime
    message = {
        'date': datetime.datetime.now(),
        'flags': 16.0,
        'from': {'id': 9999999,
                 'peer': {'access_hash': 1.0,
                          'first_name': 'Tester',
                          'last_name': 'Person',
                          'username': 'TestSender'},
                 'type': 1,
                 'type_str': 'user'},
        'id': '555',
        'out': False,
        'service': False,
        'text': '!stats',
        'to': {'id': 111111,
                'peer': {'first_name': 'Bot',
                         'last_name': 'McBot',
                         'phone': '155555555',
                         'username': 'TestBot'},
                'type': 1,
                'type_str': 'user'},
        'unread': True}

    print("Sending {0}".format(message["text"]))
    bot.on_msg_receive(message)
