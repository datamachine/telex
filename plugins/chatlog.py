import plugintypes
from DatabaseMixin import DatabaseMixin, DbType



class ChatLogPlugin(plugintypes.TelegramPlugin, DatabaseMixin):
    """
    Tracks a chat log and provides statistics and queries
    """
    patterns = [
        "^!stats"
    ]

    usage = [
        "!stats: return chat stats",
    ]

    schema = {
        'timestamp': DbType.DateTime,
        'uid': DbType.Integer,
        'chatid': DbType.Integer,
        'username': DbType.String,
        'full_name': DbType.String,
        'message': DbType.String,
    }

    def __init__(self, bot):
        super().__init__(bot)
        DatabaseMixin.__init__(self)

    def run(self, msg, matches):
        return matches.group(1)

    def pre_process(self, msg):
        self.insert(timestamp=msg["date"], uid=msg["from"]["id"],
                    chatid=msg["to"]["id"], message=msg["text"])
        return msg