class FermentationStep(object):
    def __init__(self):
        self.name = None
        # int format
        self.date = None
        self.gravity = None
        self.temp = None

    #def set_date(self, bsmx_date):
      # convert date from bsmx format (YYYY-MM-DD HH:MM:SS)
