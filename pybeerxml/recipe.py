LITERS_IN_GAL = 3.78541

def abv(og, fg):
    # src: http://www.brewunited.com/abv_calculator.php
    return (og - fg) * 131.25

def oz_to_liter(ounces):
    return (ounces/128) * LITERS_IN_GAL

def liter_to_gal(liters):
    return liters/LITERS_IN_GAL

def gravity_to_parts(gravity):
    return (gravity - 1) * 1000

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
            self.name = None
            self.bs_exp = None
            self.bxml_exp = None
            self.measured = None
            self.precision = None

        def __init__(self, name, bs_exp, bxml_exp, measured, precision=3):
            self.name = name
            self.bs_exp = bs_exp
            self.bxml_exp = bxml_exp
            self.measured = measured
            self.precision = precision

        def _delta(self, which):
            if which == "bs":
                a = self.bs_exp
            elif which == "bxml":
                a = self.bxml_exp
            else:
                print("Invalid delta type")
                return None
            b = self.measured
            if not a or not b:
                return None
            mod_a = a
            mod_b = b
            if "gravity" in self.name:
                mod_a = gravity_to_parts(a)
                mod_b = gravity_to_parts(b)
            if a > b:
                return (-1.0 * (mod_a - mod_b) / mod_a)
            return 1 + ((mod_b - mod_a) / mod_a)

        # return the delta between measured and brewsmith expected as a float
        # ie -0.05 means the measured value was 5% lower than the beersmith expected value
        @property
        def bs_delta(self):
            return self._delta("bs")

        @property
        def bxml_delta(self):
            return self._delta("bxml")

        def csv_fields(self):
            return ["bs_exp", "bxml_exp", "measured", "bs_delta", "bxml_delta"]

        def csv_values(self):
            # this ordering needs to match csv_fields
            return [self.bs_exp, self.bxml_exp, self.measured, self.bs_delta, self.bxml_delta]

        # TODO fix
        def csv_header(self):
            return "stat name,brewsmith_expected,beerxml expected,measured,beersmith_delta,beerxml_delta,precision".split(",")

        def to_list(self):
            return ([self.name, self.bs_exp, self.bxml_exp, self.measured, self.bs_delta, self.bxml_delta, self.precision])


    # generate stats for this recipe & session
    # exp vs measured
    def build_stats(self):
        # measured and expected stats
        stats = []
        # details about the brew that don't have expected
        # like equip, boil time
        details = {}
        # ident is name, date
        ident = {}
        recipe_dict = {
                'ident': ident,
                'details': details,
                'stats': stats
                }
        ident['recipe_name'] = self.name
        ident['brew_date'] = self.session.date

        details['kettle'] = self.session.equipment.name
        details['kettle_vol'] = self.session.equipment.mash_vol_g
        details['boil_time'] = self.boil_time

        stats.append(self.stat_obj("original_gravity", self.est_og, self.og, self.session.og_measured))
        stats.append(self.stat_obj("final_gravity", self.est_fg, self.fg, self.session.fg_measured))
        stats.append(self.stat_obj("abv", self.est_abv, self.abv, self.abv_measured, 1))
        stats.append(self.stat_obj("fermenter_volume_gal", liter_to_gal(self.batch_size),
                None, liter_to_gal(self.session.batch_size), 2))
        stats.append(self.stat_obj("preboil_volume_gal", self.est_boil_vol/128, None, self.session.boil_vol_measured/128, 2))
        stats.append(self.stat_obj("preboil_gravity", None, self.expected_preboil_gravity, self.session.og_boil_measured))
        stats.append(self.stat_obj("bottling_volume_gal", None, None, self.session.final_vol_measured/128, 2))
        stats.append(self.stat_obj("mash_efficiency", self.expected_mash_efficiency, None, self.measured_mash_efficiency, 2))
        stats.append(self.stat_obj("bh_efficiency", self.efficiency, None, self.measured_bhe, 2))
        max_att = 0
        for yeast in self.yeasts:
            if yeast.attenuation > max_att:
                max_att = yeast.attenuation
        stats.append(self.stat_obj("attenuation", max_att/100, None, self.session.attenuation/100, 2))
        
        stats.append(self.stat_obj(
            "eq_loss",
            liter_to_gal(self.session.exp_bh_loss(self.batch_size, self.boil_time)),
            None,
            self.session.boil_size_gal - self.session.batch_size_gal
            ))

        stats.append(self.stat_obj(
            "boil_off",
            liter_to_gal(self.session.equipment.boil_off_l(self.boil_time)),
            None,
            self.session.measured_boil_off,
            2))

        stats.append(self.stat_obj(
            "hourly_boil_off",
            liter_to_gal(self.session.equipment.boil_off_hourly_l),
            None,
            self.session.measured_hourly_boil_off(self.boil_time),
            2)) 
        
        return recipe_dict

    # refactor
    def _delta_str(self, name, a, b, prec):
        delta_format = "(Delta: %.*f [%s])"
        delta = ""
        if a:
            mod_a = a
            mod_b = b
            if "gravity" in name:
                mod_a = gravity_to_parts(a)
                mod_b = gravity_to_parts(b)
            if a > b:
                percent = "%.0f%%" % ((1 - mod_b/mod_a) * 100)
            else:
                percent = "-%.0f%%" % ((1 - mod_a/mod_b) * 100)
        return delta_format % (prec, a - b, percent)

    # TODO: fix delta formatting
    def stats_pretty(self):
        stats = self.build_stats()
        for s in stats:
            print("** %s **" % s.name)
            prec = s.precision
            delta = ""
            if s.measured:
                print("  Measured: %.*f" % (prec, s.measured))
            if s.bs_exp:
                delta = self._delta_str(s.name, s.measured, s.bs_exp, prec)
                print("  Beersmith expected: %.*f  %.0f%%" % (prec, s.bs_exp, s.bs_delta))
            if s.bxml_exp:
                delta = self._delta_str(s.name, s.measured, s.bxml_exp, prec)
                print("  BeerXML expected: %.*f  %.0f%%" % (prec, s.bxml_exp, s.bxml_delta))

    def stats_csv2(self, header=False):
        recipe_dict = self.build_stats()
        stat = []
        h = []
        if header:
            h.extend(recipe_dict['ident'].keys())
        stat.extend(recipe_dict['ident'].values())
        for s in recipe_dict['stats']:
            if header:
                for field in s.csv_fields():
                    h.append("%s_%s" % (s.name, field))
            stat.extend(s.csv_values())
        h.extend(recipe_dict['details'].keys())
        stat.extend(recipe_dict['details'].values())
        if header:
            return [h, stat]
        else:
            return [stat]


    def stats_csv(self, header=False):
        stats = self.build_stats()
        stat_csv = []
        for s in stats:
            if header:
                h = ["recipe name"]
                h.extend(s.csv_header())
                stat_csv.append(h)
                header = False
            stat = [self.name]
            stat.extend(s.to_list())
            stat_csv.append(stat)
        return stat_csv
        
    def _fermentable_points(self):
        points = 0
        for f in self.fermentables:
            points += f.points()
        return points

    @property
    def measured_bhe(self):
        m_og_pts = gravity_to_parts(self.session.og_measured)
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

    @property
    def expected_preboil_gravity(self):
        vol_g = liter_to_gal(self.batch_size + self.session.equipment.boil_off_l(self.boil_time))
        points = (self._fermentable_points() * self.efficiency) / vol_g
        return (1 + points/1000)

    # any difference from this and preboil?
    # top off I guess
    @property
    def expected_post_mash_gravity(self):
        pass

    @property
    def expected_mash_efficiency(self):
        vol = self.session.equipment.pre_boil_vol(self.batch_size, self.boil_time)
        gravity_parts = gravity_to_parts(self.expected_preboil_gravity)
        return (vol * gravity_parts) / (self.total_gu * self.batch_size)

    @expected_mash_efficiency.setter
    def expected_mash_efficiency(self, value):
        pass

    # src: https://beersmith.com/blog/2014/11/05/brewhouse-efficiency-vs-mash-efficiency-in-all-grain-beer-brewing/
    @property
    def measured_mash_efficiency(self):
        og_boil_parts = gravity_to_parts(self.session.og_boil_measured)
        return ((og_boil_parts) * self.session.boil_size_gal /
                self._fermentable_points())

    @measured_mash_efficiency.setter
    def measured_mash_efficiency(self, value):
        pass

    @property
    def total_gu(self):
        # Max efficiency points of the grain bill.
        gu = 0
        for f in self.fermentables:
            gu += f.gu(liters=self.batch_size)
        return gu

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
