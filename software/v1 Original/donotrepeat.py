class DoNotRepeat():
    def __init__(self):
        self.id = None

    def do_not_repeat(self, id):
        if self.id == id:
            return False

        self.id = id
        return True
