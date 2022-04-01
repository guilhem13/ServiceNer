import json

"""
This class return a json with id_error and its message for the user
"""
class Notification:

    id_ = None
    notification = None

    def __init__(self, id_, notification):
        self.id = id_
        self.notification = notification

    # function which create error message
    def message(self):
        return json.dumps(self.__dict__)
