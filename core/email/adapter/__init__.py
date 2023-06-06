
class Adapter:
    def __init__(self, uuid: str, request, context: dict, user):
        self.uuid = uuid
        self.request = request
        self.context = context
        self.user = user

    def send(self, to):
        raise NotImplemented
