from mmu import *
from memory import *
from faults import *
from pagetable import *


class Memory(object):
    def __init__(self, size = 20):
        self.__kernel_space = page()
        self.__user_space = [page(num) for num in range(size)]
        self.__page_table_cache = {}
        self.__free_pages = collections.deque(self.__user_space)
        self.__used = []


    def __len__(self):
        return len(self.__user_space)

    def get_free_page(self):
        try:
            pg = self.__free_pages.popleft()
        except IndexError:
            raise PageFault("Page Fault in: get_free_page()")
        else:
            return pg

    def add_free_page(self, pf):
        self.__free_pages.append(pf)

    def free_page_queue(self):
        return self.__free_pages

    def page_table_cache(self):
        return self.__page_table_cache

    def get_page_frame(self, pfn):
        return self.__user_space[pfn]








class page(object):
    def __init__(self, num = 0, data = None, free = 1):
        self.frame_num = num
        self.data = data
        self.__free = free

    def empty(self):
        return bool(self.__free)
        # return bool(self.data == None)

    def pfn(self):
        return self.frame_num

    def free(self):
        # self.data = None
        self.__free = 1

    def write_frame(self, data):
        self.data = data
        self.__free = 0

    def __repr__(self):
        return ("\n+++++++++++++++++\n"
                "PFN {}\n"
                "Data\n{}\n"
                "Free {}\n"
                "+++++++++++++++++".format(self.frame_num,
                                           self.data,
                                           self.__free))
