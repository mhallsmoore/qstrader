class Level(object):
    def __init__(self, price, volume):
        self.price = price
        self.volume = volume

    def __gt__(self, other):
        return self.price > other.price

    def __repr__(self):
        return "%s:%s" % (self.price, self.volume)
