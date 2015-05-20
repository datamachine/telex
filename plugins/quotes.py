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
        "^!delquote ([0-9]+)$",
        "^!getquote ([0-9]+)$",
        "^!findquote (.*)",
    ]

    usage = [
        "!quote: return random quote",
        "!addquote Text To Quote: add quote",
        "!quotethis: Add quote from a reply",
        "!findquote Text To Search: Search quote list, returning up to 5 answers",
        "!getquote [quote_id]: Get specific quote by id",
        "!delquote [quote_id]: (Admin) Delete quote from database",
    ]

    schema = {
        'quote_id': DbType.Integer,
        'timestamp': DbType.DateTime,
        'chat_id': DbType.Integer,
        'uid': DbType.Integer,
        'username': DbType.String,
        'full_name': DbType.String,
        'quote': DbType.String,
    }

    primary_key = 'quote_id'

    def __init__(self):
        super().__init__()
        DatabaseMixin.__init__(self)
        
    def run(self, msg, matches):
        chat_id = msg.dest.id
        if matches.group(0) == "!quote":
            return self.get_random_quote(chat_id)

        if matches.group(0) == "!quotethis":
            return self.add_reply(msg)
        
        if matches.group(0).startswith("!delquote") and self.bot.admin_check(msg):
            return self.del_quote(chat_id, matches.group(1))

        if matches.group(0).startswith("!getquote"):
            return self.get_quote(chat_id, matches.group(1))

        if matches.group(0).startswith("!findquote"):
            return self.find_quote(chat_id, matches.group(1))

        if matches.group(0).startswith("!addquote"):
            return self.add_quote(msg, matches.group(1))

    def add_quote(self, msg, quote):
        if hasattr(msg.src, 'username'):
            username = msg.src.username
        self.insert(timestamp=msg.date,
                    uid=msg.src.id, username=username,
                    full_name="{0} {1}".format(msg.src.first_name or '', msg.src.last_name or ''),
                    chat_id=msg.dest.id, quote=quote)
        return "Done!"

    def get_quote(self, chat_id, quote_id):
        results = self.query("SELECT * FROM {0} "
                             "WHERE chat_id = {1} and quote_id = ? LIMIT 1".format(self.table_name, chat_id), parameters=(quote_id,))
        if len(results) == 0:
            return "No such quote in the database for this channel!"
        result = results[0]
        text = "{quote} (#{qid} Added By {name} on {date})\n".format(quote=result["quote"],
                                                                    name=result["full_name"],
                                                                    date=datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S").date().isoformat(),
                                                                    qid=result["quote_id"])
        return text

    def find_quote(self, chat_id, search):
        results = self.query("SELECT * FROM {0} "
                             "WHERE chat_id = {1} and quote LIKE ? LIMIT 5".format(self.table_name, chat_id), parameters=("%{0}%".format(search),))

        if len(results) == 0:
            return "No such quote in the database for this channel!"
        
        text = "Quotes containing '{0}':\n".format(search)
        for result in results:
          text += "{quote} (#{qid} Added By {name} on {date})\n".format(quote=result["quote"],
                                                                       name=result["full_name"],
                                                                       date=datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S").date().isoformat(),
                                                                       qid=result["quote_id"])
        return text

    def del_quote(self, chat_id, quote_id):
        results = self.query("SELECT * FROM {0} "
                             "WHERE chat_id = {1} and quote_id = ? LIMIT 1".format(self.table_name, chat_id), parameters=(quote_id,))
        if len(results) == 0:
            return "No such quote in the database for this channel!"
        else:
            self.query("DELETE FROM {0} "
                       "WHERE chat_id = {1} and quote_id = ? LIMIT 1".format(self.table_name, chat_id), parameters=(quote_id,))
            return "Quote deleted!"     
        

    def add_reply(self, msg):
        if not hasattr(msg, 'reply_id'):
            return "The !quotethis must be used in a reply!"
        if not hasattr(msg, 'reply') or msg.reply is None:
            return "The reply is too old, cannot add it." # TODO look into fix in tgl that can't load from server
        if not hasattr(msg.reply, 'text'):
            return "Media message replys not supported currently."

        orig_peer = msg.reply.src

        quote = "{0} {1}: {2}".format(orig_peer.first_name or '', orig_peer.last_name or '', msg.reply.text)
        return self.add_quote(msg, quote)

    def get_random_quote(self, chat_id):
        results = self.query("SELECT * FROM {0} "
                             "WHERE chat_id = {1} ORDER BY RANDOM() LIMIT 1".format(self.table_name, chat_id))
        if len(results) == 0:
            return "No quotes in the database!"
        result = results[0]
        text = "{quote} (#{qid} Added By {name} on {date})\n".format(quote=result["quote"],
                                                                    name=result["full_name"],
                                                                    date=datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S").date().isoformat(),
                                                                    qid=result["quote_id"])
        return text


