import plugintypes

class ExampleCallbacksPlugin(plugintypes.TelegramPlugin):
    """
    Example demonstrating how to use callbacks
    """
    patterns = {
        "^!cb (echo) (.*)": "echo",
        "^!cb (add) ([0-9]+[.]{0,1}[0-9]*) ([0-9]+[.]{0,1}[0-9]*)": "add"
    }

    usage = [
        "!cb <echo> (.*): echoes the msg",
    ]

    def echo(self, msg, matches):
        return matches.group(2)

    def add(self, msg, matches):
        return str(float(matches.group(2)) + float(matches.group(3)))
