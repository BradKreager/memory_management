#!/usr/bin/python
import sys
import random
import time
import argparse
import collections
from operating_system import operating_system
import readline


readline.parse_and_bind("tab: complete")
parser = argparse.ArgumentParser(description='Create a data file for memory\
                                 management simulation')
parser.add_argument('input', metavar='FILE', type=str, help='input data file')
parser.add_argument('-p', '--pages', nargs='?', type=int, default=20,
                    help='sets number of physical pages')
parser.add_argument('-r', '--reclaim', action="store_true", help='Turns\
                    off reclaiming clean pages before policy reclaim')

args = parser.parse_args()

random.seed(time.time())

data_q = collections.deque()
proc_pg_max = 0



def init():
    global proc_pg_max
    try:
        if args.input:
            f = open(args.input, "r")
        else:
            f = open("memory.dat", "r")
    except IOError:
        print("file not found")
        sys.exit(1)
    else:
        jobs = f.read().splitlines()
        f.close()
        tmp = []
        for job in jobs:
            job = job.split()
            job[0] = int(job[0])
            try:
                job[2] = int(job[2])
            except:
                job.append(None)
            tmp.append(job)


        proc_pg_max = max([pg[2] for pg in tmp]) + 1
        data_q.extendleft(tmp)
        data_q.appendleft(None)



def run(input):
    global proc_pg_max
    try:
        init()

        os = operating_system(input, args.pages, proc_pg_max, args.reclaim)

        for next_action in iter(data_q.pop, None):
            # next_action = data_q.pop()
            print("next action: {}".format(next_action))
            proc_id = next_action[0]
            if next_action[1] == 'C':
                os.create_page_table(proc_id)
            elif next_action[1] == 'T':
                os.terminate_proc(proc_id)
                print("process {} terminated".format(proc_id))
            else:
                action = next_action[1]
                vpage = next_action[2]
                if action == 'A':
                    os.allocate_page(proc_id, vpage)

                elif action == 'W':
                    os.write_page(proc_id, vpage)

                elif action == 'R':
                    os.read_page(proc_id, vpage)

                else:
                    continue
    finally:
        print_results(os)



def print_results(os):
    print("\n"*3)

    print("Misses: {}".format(os.stats.misses))
    print("Cold Misses: {}".format(os.stats.cold_misses))
    print("Hits: {}".format(os.stats.hits))

    print("Hit rate: {:04.2f}%".format(os.stats.calculate_hit_rate()))
    print("Hit rate(mod cold): {:04.2f}%".format(os.stats.calculate_hit_rate_mod()))

    print("\n"*1)
    tbls = os.get_page_tables()
    for proc, tbl in tbls.items():
        print("PROCESS {}".format(proc))
        if tbl == "KILLED":
            print("{}\n".format(tbl))
        else:
            # print tbl
            for pg in tbl:
                if pg.valid() and pg.present():
                    print("\tVirtual\t{}\tPhysical\t{}".format(pg.get_vpn(),pg.get_pfn()))
                elif pg.valid() and not pg.present():
                    print("\tVirtual\t{}\tPhysical\tSwap".format(pg.get_vpn()))


if __name__ == "__main__":
    try:
        while(1):
            print("Menu (CTRL-C or 0 to exit)")
            print("0: Exit")
            print("1: FIF0")
            print("2: LRU")
            print("3: Random")
            # sim = raw_input()
            try:
                sim = input()
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("input error")
            else:
                # print type(sim)
                if sim == 0:
                    sys.exit(0)
                elif sim not in range(1,4):
                    # print("invalid input")
                    continue
                else:
                    run(sim)
                    print("run again? (y or n):")
                    ans = raw_input()
                    if ans.lower() == 'n':
                        sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception, e:
        print e
