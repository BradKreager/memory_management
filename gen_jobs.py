#!/usr/bin/python
import sys
import random
import time
import argparse
from pagetable import table as pagetable
from pagetable import phys_mem_contr as mem_controller


parser = argparse.ArgumentParser(description='Create a data file for memory\
                                 management simulation')
parser.add_argument('job_cnt', metavar='N', type=int, help='')
parser.add_argument('-p', '--pages', nargs='?', type=int, default=20, help='')
parser.add_argument('-c', '--cycles', nargs='?', type=int, default=20, help='')

args = parser.parse_args()
# print args.accumulate(args.integers)
random.seed(time.time())

proc_addr_space = args.pages / 2

n = args.job_cnt

# print n
process_ids = []
process_states = {}
process_pg_tbl = {}
pg_tbl_cache = {}
actions = ['A', 'R', 'W', 'F']
process_pg = []

history = []

memory = mem_controller(args.pages)

# print process_ids.keys()
for _ in range(0,n):
    next_procid = 0
    while next_procid in process_ids:
        # print process_ids.keys()
        next_procid = random.randint(0, 1000)

    process_states[next_procid] = 'T'
    process_ids.append(next_procid)
    pg_tbl_cache[next_procid] = pagetable(proc_addr_space)


# for x in pg_tbl_cache.values():
    # for p in x:
        # print p.valid()
        # print p

# print process_ids
# print process_states
# for x,p in pg_tbl_cache.items():
    # for i in range(0,proc_addr_space):
        # print("process: {}".format(x))
        # p[i]._print()
# print process_pg_tbl
# print process_pg

    # if(random.randint(1,4) != 1):
        # arriveTime = arriveTime + random.randint(1, 100)


try:
	# if len(sys.argv) in range(2,3):
		# f = open(sys.argv[1], "w+")
	# else:
    f = open("memory.dat", "w+")
except IOError:
	print("Error Creating File")
	sys.exit(1)

for cyc in range(args.cycles):
    page = ''
    if cyc == (args.cycles - 1):
        for term in process_ids:
            if random.randint(0,1) == 1:
                process_states[term] = 'T'
                f.write("{0}    {1}    {2}\n".format(term, \
                                                   process_states[term], \
                                                   str(page)))
                print("{0}    {1}    {2}\n".format(term, \
                                                   process_states[term], \
                                                   str(page)))
    else:
        sel_proc = random.randint(0,n-1)
        if process_states[process_ids[sel_proc]] == 'T':
            process_states[process_ids[sel_proc]] = 'C'
        elif random.randint(0,19) == 7:
                process_states[process_ids[sel_proc]] = 'T'
                # elif process_states[process_ids[sel_proc]] == 'C':
        else:
            valid_pgs = []
            for vid, p in enumerate(pg_tbl_cache[process_ids[sel_proc]]):
                if p.valid():
                    valid_pgs.append(vid)

            if random.randint(0,3) == 3:
                for _ in range(proc_addr_space):
                    page = random.randint(0,proc_addr_space - 1)
                    if page not in valid_pgs:
                        break
            else:
                if valid_pgs:
                    page = valid_pgs[random.randint(0,len(valid_pgs) - 1)]
                else:
                    page = random.randint(0,proc_addr_space - 1)

            if pg_tbl_cache[process_ids[sel_proc]][page].present() and \
               random.randint(0,25) != 11:
                next_action = actions[random.randint(1,2)]
                process_states[process_ids[sel_proc]] = next_action
                if next_action == 'W':
                    pg_tbl_cache[process_ids[sel_proc]][page].write()
                else:
                    pg_tbl_cache[process_ids[sel_proc]][page].read()

            else:
                if pg_tbl_cache[process_ids[sel_proc]][page].valid():
                    continue
                else:
                    process_states[process_ids[sel_proc]] = actions[0]
                    phys_page = memory.get_page()
                    pg_tbl_cache[process_ids[sel_proc]][page].allocate(phys_page)

        f.write("{0}    {1}    {2}\n".format(process_ids[sel_proc], \
                                           process_states[process_ids[sel_proc]], \
                                           str(page)))
        print("{0}    {1}    {2}\n".format(process_ids[sel_proc], \
                                           process_states[process_ids[sel_proc]], \
                                           str(page)))
        history.append(process_states[process_ids[sel_proc]])
    # process_pg[process_ids[sel_proc]]))

print("allocates: {}".format(history.count('A')))
print("reads: {}".format(history.count('R')))
print("writes: {}".format(history.count('W')))
print("frees: {}".format(history.count('F')))

f.close()
