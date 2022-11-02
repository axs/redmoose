from red_moose.messaging.messages import Pickle


class T:
    pass


def test_pickle_messages():
    test_obj = T()
    msg = Pickle(sender="test")
    msg.store_pickle(test_obj)
    msg_json = msg.to_json()
    msg = Pickle.from_json(msg_json)
    test_obj = msg.load_pickle()

    assert isinstance(test_obj, T)
