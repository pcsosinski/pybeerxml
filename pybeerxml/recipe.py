LITERS_IN_GAL = 3.78541

def abv(og, fg):
    # src: http://www.brewunited.com/abv_calculator.php
    return (og - fg) * 131.25

def oz_to_liter(ounces):
    return (ounces/128) * LITERS_IN_GAL

class Recipe(object):
    def __init__(self):
        self.name = None
        self.brewer = None
        self.batch_size = None
        self.boil_time = None
        self.efficiency = None
        self.primary_age = None
        self.primary_temp = None
        self.secondary_age = None
        self.secondary_temp = None
        self.tertiary_age = None
        self.tertiary_temp = None
        self.carbonation = None
        self.carbonation_temp = None
        self.age = None
        self.age_temp = None

        self.style = None
        self.hops = []
        self.yeasts = []
        self.fermentables = []
        self.miscs = []
        self.mash = None
        self.session = None
	# bsmx specific
        # volume is the estimated batch size from beersmith, in oz
        self.volume = None
        self.est_abv = None
        self.bs_actual_abv = None
        self.est_og = None
        self.og_measured = None
        self.est_fg = None
        self.bs_actual_fg = None


    @property
    def efficiency_measured(self):
        m_og_pts = (self.session.og_measured - 1) * 1000
        og_pts = (self.est_og - 1) * 1000
        return ((self.session.batch_size * m_og_pts) /
                (og_pts * self.batch_size) * self.efficiency)

    @property
    def batch_size(self):
        return oz_to_liter(self.volume)

    @property
    def abv(self):
        return abv(self.og, self.fg)

    # Gravity degrees plato approximations
    @property
    def og_plato(self):
        og = self.og or self.calc_og()
        return (-463.37) + (668.72 * og) - (205.35 * (og * og))

    @property
    def fg_plato(self):
        fg = self.fg or self.calc_fg()
        return (-463.37) + (668.72 * fg) - (205.35 * (fg * fg))

    @property
    def ibu(self):

        ibu_method = "tinseth"
        _ibu = 0.0

        for hop in self.hops:
            if hop.alpha and hop.use.lower() == "boil":
                _ibu += hop.bitterness(ibu_method, self.og, self.batch_size)

        return _ibu

    @property
    def og(self):
        _og = 1.0
        steep_efficiency = 50
        mash_efficiency = 75

        # Calculate gravities and color from fermentables
        for fermentable in self.fermentables:
            addition = fermentable.addition
            if addition == "steep":
                efficiency = steep_efficiency / 100.0
            elif addition == "mash":
                efficiency = mash_efficiency / 100.0
            else:
                efficiency = 1.0

            # Update gravities
            gu = fermentable.gu(self.batch_size) * efficiency
            gravity = gu / 1000.0
            _og += gravity

        return _og

    @property
    def fg(self):

        _fg = 0
        attenuation = 0

        # Get attenuation for final gravity
        for yeast in self.yeasts:
            if yeast.attenuation > attenuation:
                attenuation = yeast.attenuation

        if attenuation == 0:
            attenuation = 75.0

        _fg = self.og - ((self.og - 1.0) * attenuation / 100.0)

        return _fg

    @property
    def color(self):
        # Formula source: http://brewwiki.com/index.php/Estimating_Color
        mcu = 0.0
        for f in self.fermentables:
            if f.amount is not None and f.color is not None:
                # 8.3454 is conversion factor from kg/L to lb/gal
                mcu += f.amount * f.color * 8.3454 / self.batch_size
        return 1.4922 * (mcu**0.6859)

    @property
    def abv_measured(self):
        return abv(self.session.og_measured, self.session.fg_measured)

    @ibu.setter
    def ibu(self, value):
        pass

    @fg.setter
    def fg(self, value):
        pass

    @og.setter
    def og(self, value):
        pass

    @abv.setter
    def abv(self, value):
        pass

    @color.setter
    def color(self, value):
        pass

    @abv_measured.setter
    def abv_measured(self, value):
        pass

    @batch_size.setter
    def batch_size(self, value):
        pass

    @efficiency_measured.setter
    def efficiency_measured(self, value):
        pass
