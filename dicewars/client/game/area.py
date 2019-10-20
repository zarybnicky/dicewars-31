import hexutil


class Area(object):
    """Game board area
    """
    def __init__(self, name, owner, dice, neighbours, hexes):
        """
        Parameters
        ----------
        name : int
        owner : int
        dice : int
        neighbours : list of int
        hexes : list of list of int
            Hex coordinates of for all Area's hexes
        """
        self.name = int(name)
        self.owner_name = int(owner)
        self.dice = int(dice)
        self.neighbours = [int(n) for n in neighbours]
        self.hexes = [[int(i) for i in h] for h in hexes]

    def get_adjacent_areas(self):
        """Return names of adjacent areas
        """
        return self.neighbours

    def get_dice(self):
        """Return number of dice in the Area
        """
        return self.dice

    def get_name(self):
        """Return Area's name
        """
        return self.name

    def get_owner_name(self):
        """Return Area's owner's name
        """
        return self.owner_name

    def can_attack(self):
        """Return True if area has enough dice to attack
        """
        return self.dice >= 2

    def set_dice(self, dice):
        """Set area's dice
        """
        if dice < 1 or dice > 8:
            raise ValueError("Attempted to assign {} dice to Area {}".format(dice, self.name))

        self.dice = dice

    def set_owner(self, name):
        """Set owner name
        """
        self.owner_name = int(name)

    ##############
    # UI METHODS #
    ##############
    def get_hexes(self):
        """Return Hex objects of the Area
        """
        return [hexutil.Hex(h[0], h[1]) for h in self.hexes]
