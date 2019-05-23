import collections
import random
import time
from mmu import *
from memory import *
from faults import *
from pagetable import *




class operating_system(object):
    def  __init__(self, policy = 1, size = 20, paddr = 20, reclaim = False):
        self.__memory = Memory(size)
        self.__proc_addr_size = paddr
        self.__policy = policy
        # if policy == 1:
        self.swap_queue = []
        self.active_list = []
        self.clean = []
        self.MMU = MMU(self.__memory)
        self.__swap = []
        self.stats = Stats()
        self.reclaim_off = reclaim

        random.seed(time.time())



    def get_page_tables(self):
        return self.__memory.page_table_cache()


    def get_page(self):
        try:
            pg = self.__memory.get_free_page()
        except PageFault as fault:
            print fault.msg
            if not self.reclaim_off:
                if not self.reclaim():
                    self.swap_out()
            else:
                self.swap_out()

            pg = self.__memory.get_free_page()
            # print("OS retrieved PFN {}".format(pg))
        finally:
            return pg




    def create_page_table(self, base):
        size = self.__proc_addr_size
        if base in self.__memory.page_table_cache():
            if self.__memory.page_table_cache()[base] != "KILLED":
                print("page table exists")
                return
        self.__memory.page_table_cache()[base] = []
        for vpn in range(size):
            self.__memory.page_table_cache()[base].append(entry(vpn = vpn))





    def allocate_page(self, base, vpn):
        pte = self.__memory.page_table_cache()[base][vpn]
        if pte.valid():
            raise PageFault(msg="page has been previously allocated")

        pf = self.get_page()

        if not pf.empty():
            raise SegFault()
            return
        pf.write_frame(pte)
        pte.allocate(pf.pfn())
        self.add_to_swap_queue(pte)
        self.clean.append(pte)
        self.active_list.append(pte)
        self.stats.cold_misses += 1



    def update_page_references(f):
        def inner(self, *args, **kwargs):
            f(self, *args, **kwargs)
            self.update_active_list()
            self.update_clean()
        return inner


    def update_active_list(self):
        self.active_list = list(filter(lambda x: x.active(), self.active_list))

    def update_clean(self):
        self.clean = list(filter(lambda x: x.clean(), self.clean))
        self.clean.extend(list(filter(lambda x: x.clean(), self.active_list)))


    def add_to_swap_queue(self, pte):
        if pte not in self.swap_queue:
            self.swap_queue.append(pte)



    def remove_from_swap_queue(self, pte):
        if pte in self.swap_queue:
            self.swap_queue.remove(pte)



    @update_page_references
    def free_page(self, base, vpn):
        pfn = self.MMU.translate(base, vpn)
        pf = self.__memory.get_page_frame(pfn)
        self.remove_from_swap_queue(pf.data)
        pf.data.free()
        pf.free()
        self.__memory.free_page_queue().append(pf)




    @update_page_references
    def terminate_proc(self, proc_id):
        pt = self.__memory.page_table_cache()[proc_id]
        for pg in pt:
            if pg.valid() and pg.present():
                self.free_page(proc_id, pg.get_vpn())
            elif pg.valid() and not pg.present():
                self.__swap = list(filter(lambda x: x != pg, self.__swap))

        self.__memory.page_table_cache()[proc_id] = "KILLED"




    @update_page_references
    def write_page(self, base, vpn):
        try:
            pfn = self.MMU.translate(base, vpn)
        except SegFault as fault:
            self.allocate_page(base, vpn)
            pfn = self.MMU.translate(base, vpn)
        except PageFault as fault:
            try:
                pte = self.get_entry_from_swap(base, vpn)
            except SegFault as fault:
                print fault.msg
            except Exception as e:
                print "error: {}".format(e)
                raise
            self.swap_in(pte)
            pfn = self.MMU.translate(base, vpn)
            self.stats.misses += 1
        else:
            self.stats.hits += 1
        finally:
            pf = self.__memory.get_page_frame(pfn)
            pte = pf.data
            pte.write()




    def get_entry_from_swap(self, base, vpn):
        pte = self.__memory.page_table_cache()[base][vpn]
        on_disk = [pg for pg in self.__swap if pg == pte]
        self.__swap = list(filter(lambda x: x != pte, self.__swap))

        if len(on_disk) > 1:
            raise Exception("Multiple Occurances of PTE in swap.. simulation\
                            code error..")
        elif len(on_disk) != 1:
            raise SegFault("No entry in swap space")
            return
        else:
            return on_disk[0]




    @update_page_references
    def read_page(self, base, vpn):
        try:
            pfn = self.MMU.translate(base, vpn)
        except SegFault as fault:
            print fault.msg
            self.allocate_page(base, vpn)
            pfn = self.MMU.translate(base, vpn)
        except PageFault as fault:
            print fault.msg
            try:
                pte = self.get_entry_from_swap(base, vpn)
            except SegFault as fault:
                print fault.msg
            except Exception as e:
                print "error: {}".format(e)
            self.swap_in(pte)
            pfn = self.MMU.translate(base, vpn)
            self.stats.misses += 1
        else:
            self.stats.hits += 1
        finally:
            pf = self.__memory.get_page_frame(pfn)
            pte = pf.data
            pte.read()




    def reclaim(self):
        if self.clean:
            pte = self.clean[0]
            self.clean = self.clean[1:]
        else:
            pte = None
        # pte = self.MMU.scan_for_unmodified_pgs()
        if pte:
            print("Reclaiming pfn {}".format(pte.get_pfn()))
            self.swap_out_pg(pte)
            return True
        else:
            print("nothing to reclaim")
            return False


    @update_page_references
    def swap_out_pg(self, pte):
        pfn = pte.get_pfn()
        pf = self.__memory.get_page_frame(pfn)
        self.__memory.add_free_page(pf)
        pf.free()
        self.__swap.append(pte)
        pte.swap()
        self.remove_from_swap_queue(pte)
        try:
            print("+"*20)
            print("pfn {} now available".format(pfn))
            print("+"*20)
        except:
            pass


    @update_page_references
    def swap_out(self):
        self.replacement_policy(self.__policy)




    @update_page_references
    def swap_in(self, pte):
        pf = self.get_page()
        if not pf.empty():
            raise SegFault("Attempted to swap in page not marked free")
            return
        pf.write_frame(pte)
        pte.allocate(pf.pfn())
        self.add_to_swap_queue(pte)
        self.active_list.append(pte)





    def replacement_policy(self, policy):
        print("+"*20)
        sel = {
            1: self.fifo,
            2: self.lru,
            3: self.random
        }
        sel.get(policy, "No Policy Found")()



    def fifo(self):
        print("running policy: FIFO")
        pte = self.swap_queue[0]
        pfn = pte.get_pfn()
        pf = self.__memory.get_page_frame(pfn)
        self.__memory.add_free_page(pf)
        pf.free()
        self.__swap.append(pte)
        pte.swap()
        self.swap_queue = self.swap_queue[1:]
        try:
            print("+"*20)
            print("pfn {} now available".format(pfn))
            print("+"*20)
        except:
            pass



    def lru(self):
        print("running policy: LRU")
        pte = None
        if self.clean:
            pgs = iter(self.clean)
            for entry in pgs:
                if entry.accessed():
                    entry.refresh()
                else:
                    pte = entry
                    break

        elif self.active_list:
            pgs = iter(self.active_list)
            pte = self.active_list[0]
            for entry in pgs:
                if entry.accessed():
                    entry.refresh()
        else:
            raise Exception("Swap with no active jobs...")

        pfn = pte.get_pfn()
        pf = self.__memory.get_page_frame(pfn)
        self.__memory.add_free_page(pf)
        pf.free()
        self.__swap.append(pte)
        pte.swap()
        try:
            print("+"*20)
            print("pfn {} now available".format(pfn))
            print("+"*20)
        except:
            pass




    def random(self):
        print("running policy: Random")
        pfn = random.randint(0,len(self.__memory) - 1)
        pf = self.__memory.get_page_frame(pfn)
        pte = pf.data
        self.__memory.add_free_page(pf)
        pf.free()
        self.__swap.append(pte)
        pte.swap()
        # self.swap_queue = self.swap_queue[1:]
        try:
            print("+"*20)
            print("pfn {} now available".format(pfn))
            print("+"*20)
        except:
            pass




class Stats(object):
    def __init__(self):
        self.hits = 0
        self.cold_misses = 0
        self.misses = 0
        self.cache_state = []

    def __call__(self):
        pass

    def calculate_hit_rate(self):
        return ((self.hits/float(self.hits + self.misses + \
                                 self.cold_misses))*100)

    def calculate_hit_rate_mod(self):
        return (self.hits/(float(self.hits + self.misses))*100)


