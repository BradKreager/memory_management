#!/usr/bin/python
#!/usr/bin/python
import sys
import random
import time
import argparse
import collections
from pagetable import table as pagetable
from pagetable import operating_system as mem_controller
import globals as gv


# parser = argparse.ArgumentParser(description='Create a data file for memory\
                                 # management simulation')
# parser.add_argument('input', metavar='FILE', type=str, help='input data file')
# parser.add_argument('-p', '--pages', nargs='?', type=int, default=20,
                    # help='sets number of physical pages')
# parser.add_argument('-c', '--cycles', nargs='?', type=int, default=20, help='')

# args = parser.parse_args()
# random.seed(time.time())

# proc_addr_space = args.pages / 2

# n = args.job_cnt

# print n
process_ids = []
process_states = {}
process_pg_tbl = {}
pg_tbl_cache = {}
actions = ['A', 'R', 'W', 'F']
process_pg = []

data_q = collections.deque()
run_length = 0


if __name__ == "__main__":
    os = mem_controller()
    os.create_page_table(100)
    # for _ in range(24):
    os.allocate_page(100,0)
    os.read_page(100,0)
    os.write_page(100,0)
    os.free_page(100,0)

    os.read_page(100,0)

    os.swap_out()
    os.write_page(100,0)

    os.terminate_proc(100)
