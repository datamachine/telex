# Test runner for tgl module in python

on_binlog_replay_end_cb = None
on_get_difference_end_cb = None
on_our_id_cb = None
on_msg_receive_cb = None
on_secret_chat_update_cb = None
on_user_update_cb = None
on_chat_update_cb = None


def set_on_binlog_replay_end(on_binlog_replay_end):
    global on_binlog_replay_end_cb
    on_binlog_replay_end_cb = on_binlog_replay_end


def set_on_get_difference_end(on_get_difference_end):
    global on_get_difference_end_cb
    on_get_difference_end_cb = on_get_difference_end


def set_on_our_id(on_our_id):
    global on_our_id_cb
    on_our_id_cb = on_our_id


def set_on_msg_receive(on_msg_receive):
    global on_msg_receive_cb
    on_msg_receive_cb = on_msg_receive


def set_on_secret_chat_update(on_secret_chat_update):
    global on_secret_chat_update_cb
    on_secret_chat_update_cb = on_secret_chat_update


def set_on_user_update(on_user_update):
    global on_user_update_cb
    on_user_update_cb = on_user_update


def set_on_chat_update(on_chat_update):
    global on_chat_update_cb
    on_chat_update_cb = on_chat_update


def send_msg(peer_type, peer_id, msg):
    print("type: {0}, id: {1} msg:\n{2}".format(peer_type, peer_id, msg))


def mark_read(peer_type, peer_id, cb):
    pass