from telex import plugin

class EchoPlugin(plugin.TelexPlugin):
    """
    Just print the contents of the command
    """
    patterns = [
        "^{prefix}echo (.*)"
    ]

    usage = [
        "{prefix}echo msg: echoes the msg",
    ]

    def run(self, msg, matches):
        return matches.group(1)
