import plugintypes
import tgl
from DatabaseMixin import DatabaseMixin, DbType
from datetime import datetime



class QuotesPlugin(plugintypes.TelegramPlugin, DatabaseMixin):
    """
    Store and retrieve quotes from a database.
    """

    patterns = [
        "^!quote$",
        "^!addquote (.*)",
        "^!quotethis$",
    ]

    usage = [
        "!quote: return random quote",
    ]

    schema = {
        'timestamp': DbType.DateTime,
        'chat_id': DbType.Integer,
        'uid': DbType.Integer,
        'username': DbType.String,
        'full_name': DbType.String,
        'quote': DbType.String,
    }

    def __init__(self):
        super().__init__()
        DatabaseMixin.__init__(self)
        
    def run(self, msg, matches):
        if matches.group(0) == "!quote":
            return self.get_random_quote(msg["to"]["id"])
        if matches.group(0) == "!quotethis":
            return self.add_reply(msg)

        if matches.group(0).startswith("!addquote"):
            return self.add_quote(msg, matches.group(1))

    def add_quote(self, msg, quote):
        if "username" in msg["from"]["peer"]:
            username = msg["from"]["peer"]["username"]
        self.insert(timestamp=msg["date"],
                    uid=msg["from"]["id"], username=username,
                    full_name="{0} {1}".format(msg["from"]["peer"]["first_name"], msg["from"]["peer"]["last_name"]),
                    chat_id=msg["to"]["id"], quote=quote)
        return "Done!"

    def add_reply(self, msg):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(msg)
        if "reply_id" not in msg:
            return "The !quotethis must be used in a reply!"
        if "reply_to" not in msg:
            return "The reply is too old, cannot add it." # TODO look into fix in tgl that can't load from server
        if "text" not in msg["reply_to"]:
            return "Media message replys not supported currently."

        orig_peer = msg["reply_to"]["from"]["peer"]

        quote = "{0} {1}: {2}".format(orig_peer["first_name"], orig_peer["last_name"], msg["reply_to"]["text"])
        return self.add_quote(msg, quote)

    def get_random_quote(self, chat_id):
        results = self.query("SELECT * FROM {0} "
                             "WHERE chat_id = {1} ORDER BY RANDOM() LIMIT 1".format(self.table_name, chat_id))
        if len(results) == 0:
            return "No quotes in the database!"
        result = results[0]
        print(result)
        text = "{quote} (Added By {name} on {date})\n".format(quote=result["quote"],
                                                             name=result["full_name"],
                                                             date=datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S").date().isoformat())
        return text


