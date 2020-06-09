LITERS_IN_GAL = 3.78541

def gravity_to_parts(gravity):
    return (gravity - 1) * 1000

class Session(object):
    def __init__(self):
        self.name = None

        self.mash_ph = None

        # pre boil volume in OZ
        self.boil_vol_measured = None
        self.og_boil_measured = None

        self.og_measured = None
        # batch (into fermenter) volume in OZ
        self.volume_measured = None

        self.fg_measured = None
        # bottling volume in OZ
        self.final_vol_measured = None

        # bs date
        # format is YYYY-MM-DD
        self.bs_date = None

        # equipment info for session
        self.equipment = None

    def exp_bh_loss(self, batch_size, boil_length_minutes):
        return self.equipment.bh_loss(batch_size, boil_length_minutes)

    def measured_bh_loss(self):
        return self.equipment.bh_loss(self.batch_size)

    def measured_hourly_boil_off(self, boil_time_minutes):
        boil_hours = boil_time_minutes/60
        return self.measured_boil_off/boil_hours

    #(TODO) rename to into_ferm or somethng
    @property
    def batch_size(self):
        gals = self.volume_measured/128
        return gals * LITERS_IN_GAL

    @property
    def batch_size_gal(self):
        return self.volume_measured/128

    @property
    def boil_size(self):
        gals = self.boil_vol_measured/128
        return gals * LITERS_IN_GAL

    @property
    def boil_size_gal(self):
        return self.boil_vol_measured/128

    @property
    def attenuation(self):
        return ((self.og_measured - self.fg_measured) / (self.og_measured - 1)) * 100

    # (starting vol * starting gravity) / end gravity = end vol
    @property
    def measured_boil_off(self):
        end_vol = ((self.boil_size_gal * gravity_to_parts(self.og_boil_measured)) / 
                gravity_to_parts(self.og_measured))
        return self.boil_size_gal - end_vol

    @measured_boil_off.setter
    def measured_boil_off(self, value):
        pass

    @batch_size.setter
    def batch_size(self, value):
        pass

    @batch_size_gal.setter
    def batch_size_gal(self, value):
        pass

    @boil_size.setter
    def boil_size(self, value):
        pass

    @boil_size_gal.setter
    def boil_size_gal(self, value):
        pass

    @attenuation.setter
    def attenuation(self, value):
        pass


