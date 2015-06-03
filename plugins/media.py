from telex.plugin import TelexPlugin
import tgl

class MediaPlugin(TelexPlugin):
    """
    Upload media files to chat when linked.
    """
    patterns = [
        "(https?://[\w\-\_\.\?\:\/\+\=\&]+\.(gifv|gif|mp4|pdf|pdf|ogg|zip|mp3|rar|wmv|doc|avi))",
    ]

    usage = [
        "Automatically detects urls.",
    ]

    def run(self, msg, matches):
        print (matches.group(1))
        if matches.group(1).endswith("gifv"):
            return
        filename = self.bot.download_to_file(matches.group(1), matches.group(2))
        if filename:
           peer = self.bot.get_peer_to_send(msg)
           tgl.send_document(peer, filename)
