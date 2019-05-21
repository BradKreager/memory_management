class Fault(Exception):
    pass



class PageFault(Fault):
    def __init__(self, msg = "Page fault", pte = None):
        self.msg = msg
        self.pte = pte



class SegFault(Fault):
    def __init__(self, msg = "Segmentation fault", pte = None):
        self.msg = msg
        self.pte = pte
