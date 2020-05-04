import re

OZ_TO_KG = 0.0283495

class Fermentable(object):
    # Regular expressions to match for boiling sugars (DME, LME, etc).
    STEEP = re.compile("/biscuit|black|cara|chocolate|crystal|munich|roast|special|toast|victory|vienna/i")
    BOIL = re.compile("/candi|candy|dme|dry|extract|honey|lme|liquid|sugar|syrup|turbinado/i")

    def __init__(self):
        self.name = None
        # bsmx has this in oz
        self.amount = None
        self._yield = None
        self.color = None
        self._add_after_boil = None  # Should be Bool

    @property
    def amount_kg(self):
        return self.amount * OZ_TO_KG

    @amount_kg.setter
    def amount_kg(self, value):
        pass

    @property
    def add_after_boil(self):
        return bool(self._add_after_boil)

    @add_after_boil.setter
    def add_after_boil(self, value):
        self._add_after_boil = value
    
    # fucking magic number
    # probably http://howtobrew.com/book/section-2/what-is-malted-grain/table-of-typical-malt-yields
    @property
    def ppg(self):
        return 0.46214 * self._yield

    # When is this item added in the brewing process? Boil, steep, or mash?
    @property
    def addition(self):
        regexes = [
            # Forced values take precedence, then search known names and
            # default to mashing
            [re.compile("mash/i"), "mash"],
            [re.compile("steep/i"), "steep"],
            [re.compile("boil/i"), "boil"],
            [Fermentable.BOIL, "boil"],
            [Fermentable.STEEP, "steep"],
            [re.compile(".*"), "mash"]
        ]

        for regex, addition in regexes:
            try:
                if re.search(regex, self.name.lower()):
                    return addition
            except AttributeError:
                return "mash"

    # Get the gravity units for a specific liquid volume with 100% efficiency
    def gu(self, liters=1.0):
        # gu = parts per gallon * weight in pounds / gallons
        # BSMX has ounces, beerxml had KG for amounts
        #weight_lb = self.amount * 2.20462
        weight_lb = self.amount/16
        volume_gallons = liters * 0.264172
        return self.ppg * weight_lb / volume_gallons

    # return the number of points this weight of grain is capable of
    # using weight in lbs
    def points(self):
        weight_lb = self.amount/16
        return self.ppg * weight_lb

