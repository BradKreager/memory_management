from mmu import *
from memory import *
from faults import *
from pagetable import *


class MMU(object):
    def  __init__(self, memory = None):
        self.__memory = memory
        self.TLB = TLB()

    # def __getitem__(self, key):
        # return self.__page_table_cache[key]

    # def __iter__(self):
        # return iter(self.__pages)

    # def __len__(self):
        # return len(self.__pages)

    def translate(self, base, vpn):
        pt = self.__memory.page_table_cache()
        try:
            pte = pt[base][vpn]
        except:
            pass

        if not pte.valid():
            raise SegFault(pte = pte)
            return
        elif pte.present():
            return pte.get_pfn()
        else:
            raise PageFault(msg = "Page Fault in: translate()", pte = pte)

    def scan_for_unmodified_pgs(self):
        pt = self.__memory.page_table_cache()
        for proc, table in pt.items():
            if table == "KILLED":
                continue
            else:
                for pg in table:
                    if pg.valid() and pg.present() and not pg.dirty():
                        return pg

        return None


class TLB(object):
    def  __init__(self, size = 20):
        self.__size = size

    def flush(self):
        pass
