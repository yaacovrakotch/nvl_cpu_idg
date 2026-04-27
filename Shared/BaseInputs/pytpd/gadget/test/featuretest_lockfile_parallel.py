#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Runs the parallel test for lock.

Usage:
   lockfile_parallel_test.py 50     # n is number of times it will run
   ~/python/generic_nb_launch_jobs.py 1
   # above contains:
       for idx in range(200):
           nb.send_cmd('~/pytpd/main/featuretest_lockfile_parallel.py 50 %s' % idx, 'log.%s' % time.time())

   # analyze results by
   lockfile_parallel_test.py analyze <concat_resfile>
"""
import setenv      # must be first in the imports
from gadget.lockfile import Lock
from gadget.gizmo import Elapsed
import time
import sys


def get_number(starttime):
    """Get a unique number"""
    s = int(starttime) - (int(starttime) % 100000) + 0.0
    path = '/p/pde/tvpv/hsw/user_dir/jqdelosr/python/tt/number'
    with Lock(path, sleepsec=0.01) as ff:
        sw = Elapsed()
        res = int(open(path).read())
        with open(path, "w") as fho:
            fho.write(str(res + 1) + "\n")

        print("start=%.3f finish=%.3f loop=%d errloop=%d number=%d elap=%.4f" %
              (starttime - s, time.time() - s, ff.cntloop, ff.errloop, res + 1, sw.elapsed()))


def main(n):
    """main routine to launch parallel in netbatch"""
    cnt = 0
    while True:
        if int(time.time()) % 10 == 0:
            get_number(time.time())
            time.sleep(1)
            cnt += 1
            if cnt == n:
                exit(0)


import collections
from gadget.files import File
from gadget.strmore import regex, group


def analyze():
    """Given the concatenated log/*.gz files, analyze the result"""
    v_finish = []
    v_loop = []
    v_err = []
    v_num = set()
    v_start = collections.defaultdict(set)
    with File(sys.argv[2]) as fh:
        for line in fh.chomp():
            if regex(r'start=([\d\.]+) finish=([\d\.]+) loop=([\d\.]+) errloop=([\d\.]+) number=([\d\.]+)', line):
                start = float(group(1))
                v_finish.append(float(group(2)) - start)
                v_loop.append(int(group(3)))
                v_err.append(int(group(4)))
                num = group(5)
                v_start[int(start)].add(num)

                if num in v_num:
                    raise SystemExit("Error on number duplicate: [%s]" % num)
                else:
                    v_num.add(num)

            else:
                raise SystemExit("Error on [%s] line. regex failed" % line)

    print("Total:", len(v_num))
    print("chunks    :", len(v_start))
    print("count  ave:", sum(len(x) for x in v_start.values()) / len(v_start))
    print("count  max:", max(len(x) for x in v_start.values()))
    print("finish ave:", sum(v_finish) / len(v_finish))
    print("finish max:", max(v_finish))
    print("loop   ave:", sum(v_loop) / len(v_loop))
    print("loop   max:", max(v_loop))
    print("loop_e ave:", sum(v_err) / len(v_err))
    print("loop_e max:", max(v_err))
    # dumper(v_start)
    exit(0)


if len(sys.argv) == 1:
    raise SystemExit("Error: need at least one argument")

if sys.argv[1] == 'analyze':
    analyze()
elif sys.argv[1].isdigit():
    main(int(sys.argv[1]))
else:
    raise SystemExit("Error: unknown argument: %s" % sys.argv[1])


# Run through mynb (at least 100 runs): ls | mynb lockfile_parallel_test.py 10 FNAME    (note: ls is 124 files)
# concatenate all log/*.gz to one resfile
# run: lockfile_parallel_test.py analyze resfile

# Summary:
#            sec_0.01 sec_0.1 sec_0.5   (sleepsec value)
# Total        1240    1240    1240       Total jobs
# chunks        22      21       22       Total job chunks (one chunk is jobs run at the same time)
# count  ave    56      59       56       ave jobs per chunk
# count  max    85      87       87       max jobs per chunk
# finish ave     0.88    0.92     2.50    ave finish (sec)
# finish max     5.00    4.04     8.31    max finish (sec)
# loop   ave    19       7        5
# loop   max    91      26       17
# loop_e ave    4        1        1
# loop_e max    20       9       10
#
# Conclusion:
# sec_0.01 - 63 jobs/sec. --> DO NOT use (fileserver overkill)
# sec_0.1  - 64 jobs/sec. --> ok (but fileserver heavy)
# sec_0.5  - 22 jobs/sec. --> recommend normal
