import collections


class table(object):
    def __init__(self, size = 0):
        self.size = size
        self.entries = []
        self.allocated = []
        for v_id in range(0,size):
            self.entries.append(entry(vfn=v_id))

    def __getitem__(self, vfn):
        return self.entries[vfn]

    def __setitem__(self, key):
        raise Exception("Use size to resize table")

    def __delitem__(self, key):
        if key in self.entries:
            del self.entries[key]

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def __str__(self):
        s = []
        for vfn, entry in enumerate(self.entries):
            s.append("\nVFN {}\n".format(vfn))
            s.append(str(entry))
        return ''.join(s)

    def values(self):
        return self.entries

    def find_clean_pages(self):
        return [pg for pg in self.entries if pg.clean()]

    def size(self, new_size):
        old_size = self.size
        self.size = new_size
        if new_size > old_size:
            for _ in range(1,new_size):
                self.entries.append(entry())
        elif new_size < old_size and new_size > 0:
            for _ in range(1,new_size):
                del self.entries[-1]
        elif new_size == 0:
            self.entries.clear()



class entry(object):
    def __init__(self, pfn = None, vpn = None, valid = 0, dirty = 0, acc = 0, pres = 0):
        self.__PFN = pfn
        self.__VFN = vpn
        self.__valid = valid
        self.__dirty = dirty
        self.__accessed = acc
        self.__present = pres
        self.__history = []


    def clean(self):
        return bool(not self.dirty() and self.present() and self.valid())

    def active(self):
        return bool(self.valid() and self.present())

    def swapped_out(self):
        return bool(self.valid() and not self.present())

    def accessed(self):
        return bool(self.__accessed)

    def valid(self):
        return bool(self.__valid)

    def dirty(self):
        return bool(self.__dirty)

    def present(self):
        return bool(self.__present)

    def refresh(self):
        self.__accessed = 0

    def allocate(self, page):
        self.__PFN = page
        self.__valid = 1
        self.__present = 1

    def swap(self):
        if not self.valid():
            print(self.__valid)
            raise PageFault("Attempted to swap invalid virtual page", self)
        self.__PFN = None
        self.__present ^= 1
        self.__dirty = 0
        self.__accessed = 0

    def write(self):
        self.__dirty = 1
        self.__accessed = 1
        self.__history.append('W')

    def read(self):
        self.__accessed = 1
        self.__history.append('R')

    def free(self):
        self.__PFN = None
        self.__valid = 0
        self.__dirty = 0
        self.__accessed = 0
        self.__present = 0
        self.__history = []

    def get_pfn(self):
        return self.__PFN

    def get_vpn(self):
        return self.__VFN

    def __repr__(self):
        return ("PFN {}\n"
                "VFN {}\n"
                "Valid {}\n"
                "Dirty {}\n"
                "Accessed {}\n"
                "Present {}\n")\
                .format(self.__PFN,\
                        self.__VFN,\
                        self.__valid,\
                        self.__dirty,\
                        self.__accessed,\
                        self.__present)

