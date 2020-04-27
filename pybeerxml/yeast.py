class Yeast(object):
    def __init__(self):
        self.name = None
        self.type = None
        self.form = None
        self.notes = None
        self.laboratory = None
        self.product_id = None
        self.flocculation = None
        self.max_attenuation = None
        self.min_attenuation = None

    @property
    def attenuation(self):
        return (self.max_attenuation + self.min_attenuation)/2

    @attenuation.setter
    def attenuation(self, value):
        pass



