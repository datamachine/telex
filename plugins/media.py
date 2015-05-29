import plugintypes
import tgl

class MediaPlugin(plugintypes.TelegramPlugin):
    """
    Upload media files to chat when linked.
    """
    patterns = [
        "(https?://[\w\-\_\.\?\:\/\+\=\&]+\.(gif|mp4|pdf|pdf|ogg|zip|mp3|rar|wmv|doc|avi))v?",
    ]

    usage = [
        "Automatically detects urls.",
    ]

    def run(self, msg, matches):
        filename = self.bot.download_to_file(matches.group(1), matches.group(2))
        if filename:
           peer = self.bot.get_peer_to_send(msg)
           tgl.send_document(peer, filename)
