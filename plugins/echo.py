from telex import plugin
from telex.callbacks.msgreceived import command, expand

class EchoPlugin(plugin.TelexPlugin):
    
    @command('echo')
    @expand('^\S+ (?:count *= *(?P<count>\d+) |)(?P<text>.*)')
    def test_callback(self, count, text, *, bot, msg):
        if not count:
            count = 1
        if count > 20:
            self.respond_to_msg(msg, "Maximum count is 20")
        else:
            for i in range(0,int(count)):
                self.respond_to_msg(msg, text)
