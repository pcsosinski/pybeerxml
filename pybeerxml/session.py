LITERS_IN_GAL = 3.78541
 
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

    #(TODO) rename to into_ferm or somethng
    @property
    def batch_size(self):
        gals = self.final_vol_measured/128
        return gals * LITERS_IN_GAL

    @property
    def batch_size_gal(self):
        return self.final_vol_measured/128

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


