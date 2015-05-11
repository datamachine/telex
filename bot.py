import tgl


class Plugin():
    def setup(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

    def get_msg(self, msg):
        raise NotImplementedError


our_id = 0
binlog_done = False


def on_binlog_replay_end():
    global binlog_done
    binlog_done = True


def on_get_difference_end():
    pass


def on_our_id(current_id):
    global our_id
    our_id = current_id
    return "Set ID: " + str(our_id)


def on_msg_receive(msg):
    if msg["out"] and not binlog_done:
        return

    if msg["to"]["id"] == our_id:  # direct message
        ptype = msg["from"]["type"]
        pid = msg["from"]["id"]
    else:  # chat room
        ptype = msg["to"]["type"]
        pid = msg["to"]["id"]

    text = msg["text"]

    if text.startswith("!ping"):
        print("SENDING PONG")
        tgl.send_msg(ptype, pid, "PONG!")


def on_secret_chat_update(peer, types):
    return "on_secret_chat_update"


def on_user_update():
    pass


def on_chat_update():
    pass


# Set callbacks
tgl.set_on_binlog_replay_end(on_binlog_replay_end)
tgl.set_on_get_difference_end(on_get_difference_end)
tgl.set_on_our_id(on_our_id)
tgl.set_on_msg_receive(on_msg_receive)
tgl.set_on_secret_chat_update(on_secret_chat_update)
tgl.set_on_user_update(on_user_update)
tgl.set_on_chat_update(on_chat_update)


# test driver without tg running
if __name__ == "__main__":
    on_binlog_replay_end()
    on_our_id(999)

    msg = dict()
    msg["from"] = dict()
    msg["from"]["id"] = 222
    msg["from"]["type"] = 1
    msg["to"] = dict()
    msg["to"]["id"] = 333
    msg["to"]["type"] = 1
    msg["out"] = False
    msg["text"] = "!ping"

    on_msg_receive(msg)