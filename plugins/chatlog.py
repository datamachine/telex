import plugintypes
import tgl
from DatabaseMixin import DatabaseMixin, DbType
from functools import partial


class ChatLogPlugin(plugintypes.TelegramPlugin, DatabaseMixin):
    """
    Tracks a chat log and provides statistics and queries
    """
    HISTORY_QUERY_SIZE = 1000

    patterns = [
        "^!stats$",
        "^!stats_pattern (.*)",
        "^!loadhistory$"
    ]

    usage = [
        "!stats: return chat stats",
        "!stats_pattern %somepattern%: returns stats filtered by SQL LIKE style pattern",
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
        if matches.group(0).startswith("!stats_pattern"):
            return self.stats_count(msg["to"]["id"], matches.group(1))
        if matches.group(0) == "!loadhistory" and self.bot.admin_check(msg):
            return self.load_history(msg["to"]["type"], msg["to"]["id"])

    def pre_process(self, msg):
        if "media" in msg: #TODO support media
          return msg
        username = ""
        if "username" in msg["from"]["peer"]:
            username = msg["from"]["peer"]["username"]
        self.insert(msg_id=msg["id"], timestamp=msg["date"],
                    uid=msg["from"]["id"], username=username,
                    full_name="{0} {1}".format(msg["from"]["peer"]["first_name"], msg["from"]["peer"]["last_name"]),
                    chat_id=msg["to"]["id"], message=msg["text"])
        return msg

    def history_cb(self, msg_count, chat_type, chat_id, success, msgs):
        if success:
            self.insert_history(msgs)
            msg_count += len(msgs)
            if len(msgs) == self.HISTORY_QUERY_SIZE:
                tgl.get_history(chat_type, chat_id, msg_count,
                                self.HISTORY_QUERY_SIZE,
                                partial(self.history_cb, msg_count, chat_type, chat_id))
            else:
                tgl.send_msg(chat_type, chat_id, "Loaded {0} messaged into the table".format(msg_count))

    def load_history(self, chat_type, chat_id):
        msg_count = 0
        tgl.get_history(chat_type, chat_id, msg_count,
                        self.HISTORY_QUERY_SIZE,
                        partial(self.history_cb, msg_count, chat_type, chat_id))

    def insert_history(self, msgs):
        # TODO Support Media Msgs
        values = [[msg["id"], msg["date"], msg["from"]["id"], msg["from"]["peer"]["username"],
                   "{0} {1}".format(msg["from"]["peer"]["first_name"], msg["from"]["peer"]["last_name"]),
                   msg["to"]["id"], msg["text"]] for msg in msgs if "text" in msg]
        columns = ['msg_id', 'timestamp', 'uid', 'username', 'full_name', 'chat_id', 'message']

        self.insert_many(columns, values)

    def stats_count(self, chat_id, pattern=None):
        pattern_query = ""
        if pattern is not None:
            pattern_query = " AND message LIKE ? "

        query = """SELECT full_name, uid, COUNT(*) as count FROM {0}
                   WHERE uid != {1} AND chat_id = {2} {3} GROUP BY uid
                   ORDER BY count DESC""".format(self.table_name, self.bot.our_id, chat_id, pattern_query)

        if(pattern is not None):
            results = self.query(query, parameters=(pattern,))
        else:
            results = self.query(query)

        if results is None or len(results) == 0:
           return "No stats match!"

        text = "Channel Chat Statistics (count):\n"
        for result in results:
            text += "{name}: {count}\n".format(name=result["full_name"],
                                               count=result["count"])
        return text


