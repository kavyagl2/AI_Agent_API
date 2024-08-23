class StateManager:
    def __init__(self):
        self.last_poem = ""

    def update_poem(self, poem):
        self.last_poem = poem

    def get_poem(self):
        return self.last_poem

# get(2) the poem and update(1) the poem function (state.poem) get_poem and update_peom -. convert into dataclass