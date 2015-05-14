import plugintypes
from DatabaseMixin import DatabaseMixin, DbType



class ChatLogPlugin(plugintypes.TelegramPlugin, DatabaseMixin):
    """
    Tracks a chat log and provides statistics and queries
    """
    patterns = [
        "^!stats$",
        "^!loadhistory$"
    ]

    usage = [
        "!stats: return chat stats",
    ]

    schema = {
        'msg_id': DbType.Integer,
        'timestamp': DbType.DateTime,
        'uid': DbType.Integer,
        'chat_id': DbType.Integer,
        'username': DbType.String,
        'full_name': DbType.String,
        'message': DbType.String,
    }
    primary_key = 'msg_id'

    def __init__(self, bot):
        super().__init__(bot)
        DatabaseMixin.__init__(self)

    def run(self, msg, matches):
        if matches.group(0) == "!stats":
            return self.stats_count(msg["to"]["id"])

    def pre_process(self, msg):
        self.insert(msg_id=msg["id"], timestamp=msg["date"],
                    uid=msg["from"]["id"], username=msg["from"]["peer"]["username"],
                    full_name="{0} {1}".format(msg["from"]["peer"]["first_name"], msg["from"]["peer"]["last_name"]),
                    chat_id=msg["to"]["id"], message=msg["text"])
        return msg

    def stats_count(self, chat_id):
        results = self.query("SELECT full_name, uid, COUNT(*) as count FROM {0} WHERE uid != {1} AND chat_id = {2} GROUP BY uid ORDER BY count DESC".format(self.table_name, self.bot.our_id, chat_id))
        text = "Channel Chat Statistics (count):\n"
        for result in results:
            text += "{name} ({uid}): {count}\n".format(name=result["full_name"],
                                                       uid=result["uid"],
                                                       count=result["count"])
        print(text)
        return text
