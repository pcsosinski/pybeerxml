LITERS_PER_OZ = 0.0295735

class Equipment(object):
    def __init__(self):
        self.name = None
        # OZ of boil off
        # may not be per hour but just using it that way for now
        # TODO(fix that probably)
        self.boil_off = None
        # oz lost to trub
        self.trub_loss = None
        # cooling shrinkage percent
        # multiply this times post boil vol
        self.cool_pct = None
        # mash-vol is the volume of the kettle in oz
        self.mash_vol = None

    @property
    def boil_off_hourly_l(self):
        return self.boil_off * LITERS_PER_OZ

    @property
    def trub_loss_l(self):
        return self.trub_loss * LITERS_PER_OZ

    @property
    def mash_vol_g(self):
        return self.mash_vol/128

    def boil_off_l(self, boil_length_minutes):
        boil_hours = boil_length_minutes/60
        return self.boil_off_hourly_l * boil_hours

    def bh_loss(self, batch_size, boil_length_minutes):
        return self.pre_boil_vol(batch_size, boil_length_minutes) - batch_size

    def pre_boil_vol(self, batch_size, boil_length_minutes):
        # return expected pre boil volume in liters
        return self.boil_off_l(boil_length_minutes) + (batch_size + self.trub_loss_l) / (1 - self.cool_pct/100)

    def total_water_vol(self, batch_size, boil_length_minutes, mash_absorbtion):
        # return total water volume in liters
        return self.pre_boil_vol(batch_size, boil_length_minutes) + mash_absorbtion

