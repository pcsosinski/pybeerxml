LITERS_IN_GAL = 3.78541

def abv(og, fg):
    # src: http://www.brewunited.com/abv_calculator.php
    return (og - fg) * 131.25

def oz_to_liter(ounces):
    return (ounces/128) * LITERS_IN_GAL

def liter_to_gal(liters):
    return liters/LITERS_IN_GAL

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
        # into the fermenter
        self.volume = None
        # boil_vol is the estimaed boil volume, in oz
        self.est_boil_vol = None
        self.est_abv = None
        self.est_og = None
        self.og_measured = None
        self.est_fg = None


    # stat object for recipe.  not sure if this is overkill.
    class stat_obj(object):
        def __init__(self):
            self.bs_exp = None
            self.bxml_exp = None
            self.measured = None
            self.precision = None

        def __init__(self, bs_exp, bxml_exp, measured, precision=3):
            self.bs_exp = bs_exp
            self.bxml_exp = bxml_exp
            self.measured = measured
            self.precision = precision

    # generate stats for this recipe & session
    # exp vs measured
    def build_stats(self):
        stats = {}

        stats["original_gravity"] = self.stat_obj(self.est_og, self.og, self.session.og_measured)
        stats["final_gravity"] = self.stat_obj(self.est_fg, self.fg, self.session.fg_measured)
        stats["abv"] = self.stat_obj(self.est_abv, self.abv, self.abv_measured, 1)
        stats["fermenter_volume_gal"] = self.stat_obj(liter_to_gal(self.batch_size),
                None, liter_to_gal(self.session.batch_size), 2)
        stats["preboil_volume_gal"] = self.stat_obj(self.est_boil_vol/128, None, self.session.boil_vol_measured/128, 2)
        stats["preboil_gravity"] = self.stat_obj(None, None, self.session.og_boil_measured)
        stats["bottling_volume_gal"] = self.stat_obj(None, None, self.session.final_vol_measured/128, 2)
        stats["mash_efficiency"] = self.stat_obj(self.expected_mash_efficiency, None, self.measured_mash_efficiency, 2)
        stats["bh_efficiency"] = self.stat_obj(self.efficiency, None, self.measured_bhe, 2)
        max_att = 0
        for yeast in self.yeasts:
            if yeast.attenuation > max_att:
                max_att = yeast.attenuation
        stats["attenuation"] = self.stat_obj(max_att/100, None, self.session.attenuation/100, 2)

        return stats

    # refactor
    def _delta_str(self, name, a, b, prec):
        delta_format = "(Delta: %.*f [%s])"
        delta = ""
        if a:
            mod_a = a
            mod_b = b
            if "gravity" in name:
                mod_a = self.gravity_to_parts(a)
                mod_b = self.gravity_to_parts(b)
            if a > b:
                percent = "%.0f%%" % ((1 - mod_b/mod_a) * 100)
            else:
                percent = "-%.0f%%" % ((1 - mod_a/mod_b) * 100)
        return delta_format % (prec, a - b, percent)

    def stats_pretty(self):
        stats = self.build_stats()
        for s, i in stats.items():
            print("** %s **" % s)
            prec = i.precision
            delta = ""
            if i.measured:
                print("  Measured: %.*f" % (prec, i.measured))
            if i.bs_exp:
                delta = self._delta_str(s, i.measured, i.bs_exp, prec)
                print("  Beersmith expected: %.*f  %s" % (prec, i.bs_exp, delta))
            if i.bxml_exp:
                delta = self._delta_str(s, i.measured, i.bxml_exp, prec)
                print("  BeerXML expected: %.*f  %s" % (prec, i.bxml_exp, delta))


        
    def _fermentable_points(self):
        points = 0
        for f in self.fermentables:
            points += f.points()
        return points

    @property
    def measured_bhe(self):
        m_og_pts = self.gravity_to_parts(self.session.og_measured)
        return ((self.session.batch_size_gal * m_og_pts) /
                self._fermentable_points())

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

    #TODO  move to support lib
    def gravity_to_parts(self, gravity):
        return (gravity - 1) * 1000

    #TODO figure out how brewsmith does this, probably some calculation of potential with boil off, based on Brewhouse.  ugg.
    @property
    def expected_mash_efficiency(self):
        est_og_parts = self.gravity_to_parts(self.est_og)
        est_boil_gal = self.est_boil_vol/128 
        return (est_og_parts * est_boil_gal / self._fermentable_points())

    @expected_mash_efficiency.setter
    def expected_mash_efficiency(self, value):
        pass

    # src: https://beersmith.com/blog/2014/11/05/brewhouse-efficiency-vs-mash-efficiency-in-all-grain-beer-brewing/
    @property
    def measured_mash_efficiency(self):
        og_boil_parts = self.gravity_to_parts(self.session.og_boil_measured)
        return ((og_boil_parts) * self.session.boil_size_gal /
                self._fermentable_points())

    @measured_mash_efficiency.setter
    def measured_mash_efficiency(self, value):
        pass

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

    @measured_bhe.setter
    def measured_bhe(self, value):
        pass
