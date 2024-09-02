# Copyright (c) 2013-2020 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2006-2008 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse

import m5
from m5.defines import buildEnv
from m5.objects import *

from common.Benchmarks import *
from common import ObjectList

vio_9p_help = """\
Enable the Virtio 9P device and set the path to share. The default 9p path is
m5ou5/9p/share, and it can be changed by setting VirtIO9p.root with --param. A
sample guest mount command is: "mount -t 9p -o
trans=virtio,version=9p2000.L,aname=<host-full-path> gem5 /mnt/9p" where
"<host-full-path>" is the full path being shared on the host, and "gem5" is a
fixed mount tag. This option requires the diod 9P server to be installed in the
host PATH or selected with with: VirtIO9PDiod.diod.
"""


class ListCpu(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.cpu_list.print()
        sys.exit(0)


class ListBp(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.bp_list.print()
        sys.exit(0)


class ListHWP(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.hwp_list.print()
        sys.exit(0)


class ListRP(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.rp_list.print()
        sys.exit(0)


class ListIndirectBP(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.indirect_bp_list.print()
        sys.exit(0)


class ListMem(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.mem_list.print()
        sys.exit(0)


class ListPlatform(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ObjectList.platform_list.print()
        sys.exit(0)

# Add the very basic options that work also in the case of the no ISA
# being used, and consequently no CPUs, but rather various types of
# testers and traffic generators.


def addNoISAOptions(parser):
    parser.add_argument("--perf-io", type=str, default="False")
    parser.add_argument("--num-nics", type=int, default=1)
    # For all loadgens:
    parser.add_argument("--num-loadgens", type=int, default=0)
    parser.add_argument("--loadgen-type", type=str, default="Simple")
    parser.add_argument("--packet-rate", type=int, default=1)
    parser.add_argument("--loadgen-start", type=int, default=1)
    parser.add_argument("--loadgen-stop", type=int, default=m5.MaxTick)
    # For Simple loadgen:
    parser.add_argument("--loadgen-mode", type=str, default="Static")
    parser.add_argument("--packet-size", type=int, default=128)
    # For Pcap loadgen:
    parser.add_argument("--loadgen-stack", type=str, default="KernelStack")
    parser.add_argument("--loadgen_pcap_filename", type=str, default="")
    parser.add_argument("--loadgen-replymode", type=str, default="ReplyAndAdjustThroughput")
    parser.add_argument("--loadgen-port-filter", type=int, default=1)
    parser.add_argument("--loadgen-increment-interval", type=int, default=1)

    parser.add_argument("-n", "--num-cpus", type=int, default=1)
    parser.add_argument("--sys-voltage", action="store", type=str,
                        default='1.0V',
                        help="""Top-level voltage for blocks running at system
                      power supply""")
    parser.add_argument("--sys-clock", action="store", type=str,
                        default='1GHz',
                        help="""Top-level clock for blocks running at system
                      speed""")

    # Memory Options
    parser.add_argument("--list-mem-types",
                        action=ListMem, nargs=0,
                        help="List available memory types")
    parser.add_argument("--mem-type", default="DDR3_1600_8x8",
                        choices=ObjectList.mem_list.get_names(),
                        help="type of memory to use")
    parser.add_argument("--mem-channels", type=int, default=1,
                        help="number of memory channels")
    parser.add_argument("--mem-ranks", type=int, default=None,
                        help="number of memory ranks per channel")
    parser.add_argument(
        "--mem-size", action="store", type=str, default="512MB",
        help="Specify the physical memory size (single memory)")
    parser.add_argument("--enable-dram-powerdown", action="store_true",
                        help="Enable low-power states in DRAMInterface")
    parser.add_argument("--mem-channels-intlv", type=int, default=0,
                        help="Memory channels interleave")

    parser.add_argument("--memchecker", action="store_true")

    # Cache Options
    parser.add_argument("--external-memory-system", type=str,
                        help="use external ports of this port_type for caches")
    parser.add_argument("--tlm-memory", type=str,
                        help="use external port for SystemC TLM cosimulation")
    parser.add_argument("--caches", action="store_true")
    parser.add_argument("--l2cache", action="store_true")
    parser.add_argument("--l3cache", action="store_true")     # SHIN. Add an L3 option
    parser.add_argument("--num-dirs", type=int, default=1)
    parser.add_argument("--num-l2caches", type=int, default=1)
    parser.add_argument("--num-l3caches", type=int, default=1)
    parser.add_argument("--l1d_size", type=str, default="64kB")
    parser.add_argument("--l1i_size", type=str, default="32kB")
    parser.add_argument("--l2_size", type=str, default="2MB")
    parser.add_argument("--l3_size", type=str, default="16MB")
    parser.add_argument("--l1d_assoc", type=int, default=2)
    parser.add_argument("--l1i_assoc", type=int, default=2)
    parser.add_argument("--l2_assoc", type=int, default=8)
    parser.add_argument("--l3_assoc", type=int, default=16)
    parser.add_argument("--cacheline_size", type=int, default=64)

    # Enable Ruby
    parser.add_argument("--ruby", action="store_true")

    # Run duration options
    parser.add_argument("-m", "--abs-max-tick", type=int, default=m5.MaxTick,
                        metavar="TICKS", help="Run to absolute simulated tick "
                        "specified including ticks from a restored checkpoint")
    parser.add_argument(
        "--rel-max-tick", type=int, default=None, metavar="TICKS",
        help="Simulate for specified number of"
        " ticks relative to the simulation start tick (e.g. if "
        "restoring a checkpoint)")
    parser.add_argument("--maxtime", type=float, default=None,
                        help="Run to the specified absolute simulated time in "
                        "seconds")
    parser.add_argument(
        "-P", "--param", action="append", default=[],
        help="Set a SimObject parameter relative to the root node. "
        "An extended Python multi range slicing syntax can be used "
        "for arrays. For example: "
        "'system.cpu[0,1,3:8:2].max_insts_all_threads = 42' "
        "sets max_insts_all_threads for cpus 0, 1, 3, 5 and 7 "
        "Direct parameters of the root object are not accessible, "
        "only parameters of its children.")

# Add common options that assume a non-NULL ISA.


def addCommonOptions(parser):
    # start by adding the base options that do not assume an ISA
    addNoISAOptions(parser)

    # system options
    parser.add_argument("--list-cpu-types",
                        action=ListCpu, nargs=0,
                        help="List available CPU types")
    parser.add_argument("--cpu-type", default="AtomicSimpleCPU",
                        choices=ObjectList.cpu_list.get_names(),
                        help="type of cpu to run with")
    parser.add_argument("--list-bp-types",
                        action=ListBp, nargs=0,
                        help="List available branch predictor types")
    parser.add_argument("--list-indirect-bp-types",
                        action=ListIndirectBP, nargs=0,
                        help="List available indirect branch predictor types")
    parser.add_argument("--bp-type", default=None,
                        choices=ObjectList.bp_list.get_names(),
                        help="""
                        type of branch predictor to run with
                        (if not set, use the default branch predictor of
                        the selected CPU)""")
    parser.add_argument("--indirect-bp-type", default=None,
                        choices=ObjectList.indirect_bp_list.get_names(),
                        help="type of indirect branch predictor to run with")

    parser.add_argument("--list-rp-types",
                        action=ListRP, nargs=0,
                        help="List available replacement policy types")

    parser.add_argument("--list-hwp-types",
                        action=ListHWP, nargs=0,
                        help="List available hardware prefetcher types")
    parser.add_argument("--l1i-hwp-type", default=None,
                        choices=ObjectList.hwp_list.get_names(),
                        help="""
                        type of hardware prefetcher to use with the L1
                        instruction cache.
                        (if not set, use the default prefetcher of
                        the selected cache)""")
    parser.add_argument("--l1d-hwp-type", default=None,
                        choices=ObjectList.hwp_list.get_names(),
                        help="""
                        type of hardware prefetcher to use with the L1
                        data cache.
                        (if not set, use the default prefetcher of
                        the selected cache)""")
    parser.add_argument("--l2-hwp-type", default=None,
                        choices=ObjectList.hwp_list.get_names(),
                        help="""
                        type of hardware prefetcher to use with the L2 cache.
                        (if not set, use the default prefetcher of
                        the selected cache)""")
    parser.add_argument("--checker", action="store_true")
    parser.add_argument("--cpu-clock", action="store", type=str,
                        default='2GHz',
                        help="Clock for blocks running at CPU speed")
    parser.add_argument("--smt", action="store_true", default=False,
                        help="""
                      Only used if multiple programs are specified. If true,
                      then the number of threads per cpu is same as the
                      number of programs.""")
    parser.add_argument("--smt-model", action="store_true", default=False,
                        help="""
                      Only used if multiple programs are specified. If true,
                      then the number of threads per cpu is same as the
                      number of programs.""")
    parser.add_argument(
        "--elastic-trace-en", action="store_true",
        help="""Enable capture of data dependency and instruction
                      fetch traces using elastic trace probe.""")
    # Trace file paths input to trace probe in a capture simulation and input
    # to Trace CPU in a replay simulation
    parser.add_argument("--inst-trace-file", action="store", type=str,
                        help="""Instruction fetch trace file input to
                      Elastic Trace probe in a capture simulation and
                      Trace CPU in a replay simulation""", default="")
    parser.add_argument("--data-trace-file", action="store", type=str,
                        help="""Data dependency trace file input to
                      Elastic Trace probe in a capture simulation and
                      Trace CPU in a replay simulation""", default="")

    parser.add_argument("-l", "--lpae", action="store_true")
    parser.add_argument("-V", "--virtualisation", action="store_true")

    # dist-gem5 options
    parser.add_argument("--dist", action="store_true",
                        help="Parallel distributed gem5 simulation.")
    parser.add_argument(
        "--dist-sync-on-pseudo-op", action="store_true",
        help="Use a pseudo-op to start dist-gem5 synchronization.")
    parser.add_argument(
        "--is-switch", action="store_true",
        help="Select the network switch simulator process for a"
        "distributed gem5 run")
    parser.add_argument("--dist-rank", default=0, action="store", type=int,
                        help="Rank of this system within the dist gem5 run.")
    parser.add_argument(
        "--dist-size", default=0, action="store", type=int,
        help="Number of gem5 processes within the dist gem5 run.")
    parser.add_argument(
        "--dist-server-name", default="127.0.0.1", action="store", type=str,
        help="Name of the message server host\nDEFAULT: localhost")
    parser.add_argument("--dist-server-port",
                        default=2200,
                        action="store", type=int,
                        help="Message server listen port\nDEFAULT: 2200")
    parser.add_argument(
        "--dist-sync-repeat", default="0us", action="store", type=str,
        help="Repeat interval for synchronisation barriers among "
        "dist-gem5 processes\nDEFAULT: --ethernet-linkdelay")
    parser.add_argument(
        "--dist-sync-start", default="10000000000t", action="store",
        type=str,
        help="Time to schedule the first dist synchronisation barrier\n"
        "DEFAULT:10000000000t")
    parser.add_argument("--ethernet-linkspeed", default="100Gbps",
                        action="store", type=str,
                        help="Link speed in bps\nDEFAULT: 10Gbps")
    parser.add_argument("--ethernet-linkdelay", default="10us",
                        action="store", type=str,
                        help="Link delay in seconds\nDEFAULT: 10us")

 

    # Run duration options
    parser.add_argument("-I", "--maxinsts", action="store", type=int,
                        default=None, help="""Total number of instructions to
                                            simulate (default: run forever)""")
    parser.add_argument("--work-item-id", action="store", type=int,
                        help="the specific work id for exit & checkpointing")
    parser.add_argument("--num-work-ids", action="store", type=int,
                        help="Number of distinct work item types")
    parser.add_argument("--work-begin-cpu-id-exit", action="store", type=int,
                        help="exit when work starts on the specified cpu")
    parser.add_argument("--work-end-exit-count", action="store", type=int,
                        help="exit at specified work end count")
    parser.add_argument("--work-begin-exit-count", action="store", type=int,
                        help="exit at specified work begin count")
    parser.add_argument("--init-param", action="store", type=int, default=0,
                        help="""Parameter available in simulation with m5
                              initparam""")
    parser.add_argument("--init-param-drive", action="store", type=int, default=1)

    parser.add_argument(
        "--initialize-only", action="store_true", default=False,
        help="""Exit after initialization. Do not simulate time.
                              Useful when gem5 is run as a library.""")

    # Simpoint options
    parser.add_argument("--simpoint-profile", action="store_true",
                        help="Enable basic block profiling for SimPoints")
    parser.add_argument("--simpoint-interval", type=int, default=10000000,
                        help="SimPoint interval in num of instructions")
    parser.add_argument(
        "--take-simpoint-checkpoints", action="store", type=str,
        help="<simpoint file,weight file,interval-length,warmup-length>")
    parser.add_argument("--restore-simpoint-checkpoint", action="store_true",
                        default=False,
                        help="restore from a simpoint checkpoint taken with " +
                        "--take-simpoint-checkpoints")

    # Checkpointing options
    # Note that performing checkpointing via python script files will override
    # checkpoint instructions built into binaries.
    parser.add_argument(
        "--take-checkpoints", action="store", type=str,
        help="<M,N> take checkpoints at tick M and every N ticks thereafter")
    parser.add_argument(
        "--max-checkpoints", action="store", type=int,
        help="the maximum number of checkpoints to drop", default=5)
    parser.add_argument(
        "--checkpoint-dir", action="store", type=str,
        help="Place all checkpoints in this absolute directory")
    parser.add_argument("-r", "--checkpoint-restore", action="store", type=int,
                        help="restore from checkpoint <N>")
    parser.add_argument("--checkpoint-at-end", action="store_true",
                        help="take a checkpoint at end of run")
    parser.add_argument(
        "--work-begin-checkpoint-count", action="store", type=int,
        help="checkpoint at specified work begin count")
    parser.add_argument(
        "--work-end-checkpoint-count", action="store", type=int,
        help="checkpoint at specified work end count")
    parser.add_argument(
        "--work-cpus-checkpoint-count", action="store", type=int,
        help="checkpoint and exit when active cpu count is reached")
    parser.add_argument("--restore-with-cpu", action="store",
                        default="AtomicSimpleCPU",
                        choices=ObjectList.cpu_list.get_names(),
                        help="cpu type for restoring from a checkpoint")

    # CPU Switching - default switch model goes from a checkpoint
    # to a timing simple CPU with caches to warm up, then to detailed CPU for
    # data measurement
    parser.add_argument(
        "--repeat-switch", action="store", type=int, default=None,
        help="switch back and forth between CPUs with period <N>")
    parser.add_argument(
        "-s", "--standard-switch", action="store", type=int, default=None,
        help="switch from timing to Detailed CPU after warmup period of <N>")
    parser.add_argument("-p", "--prog-interval", type=str,
                        help="CPU Progress Interval")

    # Fastforwarding and simpoint related materials
    parser.add_argument(
        "-W", "--warmup-insts", action="store", type=int, default=None,
        help="Warmup period in total instructions (requires --standard-switch)")
    parser.add_argument(
        "--bench", action="store", type=str, default=None,
        help="base names for --take-checkpoint and --checkpoint-restore")
    parser.add_argument(
        "-F", "--fast-forward", action="store", type=str, default=None,
        help="Number of instructions to fast forward before switching")
    parser.add_argument(
        "-S", "--simpoint", action="store_true", default=False,
        help="""Use workload simpoints as an instruction offset for
                --checkpoint-restore or --take-checkpoint.""")
    parser.add_argument(
        "--at-instruction", action="store_true", default=False,
        help="""Treat value of --checkpoint-restore or --take-checkpoint as a
                number of instructions.""")
    parser.add_argument("--spec-input", default="ref",
                        choices=["ref", "test", "train", "smred", "mdred",
                                 "lgred"],
                        help="Input set size for SPEC CPU2000 benchmarks.")
    parser.add_argument("--arm-iset", default="arm",
                        choices=["arm", "thumb", "aarch64"],
                        help="ARM instruction set.")
    parser.add_argument(
        "--stats-root", action="append", default=[],
        help="If given, dump only stats of objects under the given SimObject. "
        "SimObjects are identified with Python notation as in: "
        "system.cpu[0].mmu. All elements of an array can be selected at "
        "once with: system.cpu[:].mmu. If given multiple times, dump stats "
        "that are present under any of the roots. If not given, dump all "
        "stats. ")

    parser.add_argument(
        "--warmup-dpdk", action="store", type=int, default=0,
        help="Warmup period in ticks (requires --standard-switch)")
    
    # SHIN. DDIO(and IDIO) related
    parser.add_argument("--ddio-disabled", action="store_true",
                      help="DDIO is disabled")

    parser.add_argument("--ddio-enabled", action="store_true",
                      help="Enable DDIO")
    parser.add_argument("--ddio-way-part", action="store", type=int,
        help="way partion of ddio - if set to 0 ddio can use the entire llc", default=0)
    parser.add_argument("--iocache_size", type=str, default="1kB")
    parser.add_argument("--iocache_assoc", type=int, default=16)

    # SHIN. DDIO pass to MLC/LLC/Mem
    parser.add_argument("--mlc-adaptive-ddio", action="store_true", help="Enable MLC/LLC/Mem bypass")
    parser.add_argument("--disable-snoop-filter", action="store_true")

    # SHIN. Adaptive DDIO test option
    parser.add_argument("--do-not-pass-to-mlc", action="store_true", default=False,
                        help="For testing. Do not send to MLC from DdioBridge")
    parser.add_argument("--snoop-via-memside", action="store_true", default=False,
                        help="For testing. Using memsideport for snooping on DdioBridge")
    parser.add_argument("--normal-dma-mode", action="store_true", default=False,
                        help="For testing. Ignore all masterport except memside")

    # SHIN. AdpativeDDIO test option
    # parser.add_argument("--ddio-flag", action="store", type=int, help="DDIO path test option")
    parser.add_argument("--tracefile0", action="store", type=str, default='', help = "For timer")
    parser.add_argument("--tracefile1", action="store", type=str, default='', help = "For timer")
    parser.add_argument("--tracefile2", action="store", type=str, default='', help = "For timer")
    parser.add_argument("--tracefile3", action="store", type=str, default='', help = "For timer")

    parser.add_argument("--use-loadgenerator", action="store_true", help="Enable Usegen")


    # SHIN. Run APP option
    #parser.add_argument("--workloads", action="store", type=int, help="App option")

    # # SHIN. WordCount Text
    # parser.add_argument("--wordcount0", action="store", type=str, default='', help = "For WordCount")
    # parser.add_argument("--wordcount1", action="store", type=str, default='', help = "For WordCount")
    # parser.add_argument("--wordcount2", action="store", type=str, default='', help = "For WordCount")
    # parser.add_argument("--wordcount3", action="store", type=str, default='', help = "For WordCount")

    # # SHIN. Key-Value Store
    # parser.add_argument("--keyvalue0", action="store", type=str, default='', help = "For Key-Value Store")
    # parser.add_argument("--keyvalue1", action="store", type=str, default='', help = "For Key-Value Store")
    # parser.add_argument("--keyvalue2", action="store", type=str, default='', help = "For Key-Value Store")
    # parser.add_argument("--keyvalue3", action="store", type=str, default='', help = "For Key-Value Store")

    # parser.add_argument("--searchtree0", action="store", type=str, default='', help = "For Loading SearchTree of Key-Value Store")
    # parser.add_argument("--searchtree1", action="store", type=str, default='', help = "For Loading SearchTree of Key-Value Store")
    # parser.add_argument("--searchtree2", action="store", type=str, default='', help = "For Loading SearchTree of Key-Value Store")
    # parser.add_argument("--searchtree3", action="store", type=str, default='', help = "For Loading SearchTree of Key-Value Store")

    # # SHIN. Workload RPS
    # parser.add_argument("--rps0", action="store", type=int, help="Workload RPS")
    # parser.add_argument("--rps1", action="store", type=int, help="Workload RPS")
    # parser.add_argument("--rps2", action="store", type=int, help="Workload RPS")
    # parser.add_argument("--rps3", action="store", type=int, help="Workload RPS")

    # # SHIN. WarmUp RPS
    # parser.add_argument("--rps0warmup", action="store", type=int, help="Warmup RPS")
    # parser.add_argument("--rps1warmup", action="store", type=int, help="Warmup RPS")
    # parser.add_argument("--rps2warmup", action="store", type=int, help="Warmup RPS")
    # parser.add_argument("--rps3warmup", action="store", type=int, help="Warmup RPS")

    # # SHIN. WarmUp Time
    # parser.add_argument("--warmuptime0", action="store", type=int, help="Warmup Time")
    # parser.add_argument("--warmuptime1", action="store", type=int, help="Warmup Time")
    # parser.add_argument("--warmuptime2", action="store", type=int, help="Warmup Time")
    # parser.add_argument("--warmuptime3", action="store", type=int, help="Warmup Time")

    # SHIN. Dynamic
    parser.add_argument("--ddio_option_app0", action="store", type=int, help="Ddio Options")
    parser.add_argument("--ddio_option_app1", action="store", type=int, help="Ddio Options")
    parser.add_argument("--ddio_option_app2", action="store", type=int, help="Ddio Options")
    parser.add_argument("--ddio_option_app3", action="store", type=int, help="Ddio Options")
    parser.add_argument("--dynamic_ddio", action="store", type=int, help="Ddio Options")

    parser.add_argument("--window_size", action="store", type=int, help="Window size for Forworad select (us)")
    parser.add_argument("--threshhold_otf", action="store", type=float, help="Thresh hold for bypass cache")
    parser.add_argument("--threshhold_gradchange", action="store", type=float, help="Thresh hold for bypass cache")
    parser.add_argument("--threshhold_abs", action="store", type=float, help="Thresh hold for bypass cache")

    # SHIN. Pesudo SMT
    parser.add_argument("--share-l2", action="store", type=int, help="Enable MLC/LLC/Mem bypass")

    # SHIN. Prefetcher hint
    parser.add_argument("--send-prefetch-hint", action="store", type=int, help="Enable MLC Prefetchermode")
    parser.add_argument("--send-header-only", action="store", type=int, help="Send Hint Only")


def addSEOptions(parser):
    # Benchmark options
    parser.add_argument("-c", "--cmd", default="",
                        help="The binary to run in syscall emulation mode.")
    parser.add_argument("-o", "--options", default="",
                        help="""The options to pass to the binary, use " "
                              around the entire string""")
    parser.add_argument("-e", "--env", default="",
                        help="Initialize workload environment from text file.")
    parser.add_argument("-i", "--input", default="",
                        help="Read stdin from a file.")
    parser.add_argument("--output", default="",
                        help="Redirect stdout to a file.")
    parser.add_argument("--errout", default="",
                        help="Redirect stderr to a file.")
    parser.add_argument("--chroot", action="store", type=str, default=None,
                        help="The chroot option allows a user to alter the "
                        "search path for processes running in SE mode. "
                        "Normally, the search path would begin at the "
                        "root of the filesystem (i.e. /). With chroot, "
                        "a user can force the process to begin looking at"
                        "some other location (i.e. /home/user/rand_dir)."
                        "The intended use is to trick sophisticated "
                        "software which queries the __HOST__ filesystem "
                        "for information or functionality. Instead of "
                        "finding files on the __HOST__ filesystem, the "
                        "process will find the user's replacment files.")
    parser.add_argument("--interp-dir", action="store", type=str,
                        default=None,
                        help="The interp-dir option is used for "
                        "setting the interpreter's path. This will "
                        "allow to load the guest dynamic linker/loader "
                        "itself from the elf binary. The option points to "
                        "the parent folder of the guest /lib in the "
                        "host fs")

    parser.add_argument("--redirects", action="append", type=str,
                        default=[],
                        help="A collection of one or more redirect paths "
                        "to be used in syscall emulation."
                        "Usage: gem5.opt [...] --redirects /dir1=/path/"
                        "to/host/dir1 --redirects /dir2=/path/to/host/dir2")
    parser.add_argument("--wait-gdb", default=False, action='store_true',
                        help="Wait for remote GDB to connect.")


def addFSOptions(parser):
    from common.FSConfig import os_types

    # Simulation options
    parser.add_argument(
        "--timesync", action="store_true",
        help="Prevent simulated time from getting ahead of real time")

    # System options
    parser.add_argument("--kernel", action="store", type=str)
    parser.add_argument("--os-type", action="store",
                        choices=os_types[str(buildEnv['TARGET_ISA'])],
                        default="linux",
                        help="Specifies type of OS to boot")
    parser.add_argument("--script", action="store", type=str)
    parser.add_argument("--drivenode-script", action="store", type=str, 
        help="specifies the script to be loaded in the drive_system for "
        "dual mode gem5")
    parser.add_argument(
        "--frame-capture", action="store_true",
        help="Stores changed frame buffers from the VNC server to compressed "
        "files in the gem5 output directory")

    if buildEnv['TARGET_ISA'] == "arm":
        parser.add_argument(
            "--bare-metal", action="store_true",
            help="Provide the raw system without the linux specific bits")
        parser.add_argument("--list-machine-types",
                            action=ListPlatform, nargs=0,
                            help="List available platform types")
        parser.add_argument("--machine-type", action="store",
                            choices=ObjectList.platform_list.get_names(),
                            default="VExpress_GEM5_V1")
        parser.add_argument(
            "--dtb-filename", action="store", type=str,
            help="Specifies device tree blob file to use with device-tree-"
            "enabled kernels")
        parser.add_argument(
            "--enable-security-extensions", action="store_true",
            help="Turn on the ARM Security Extensions")
        parser.add_argument(
            "--enable-context-switch-stats-dump", action="store_true",
            help="Enable stats dump at context "
            "switches and dump tasks file (required for Streamline)")
        parser.add_argument("--vio-9p", action="store_true", help=vio_9p_help)
        parser.add_argument(
            "--bootloader", action='append',
            help="executable file that runs before the --kernel")

    # Benchmark options
    parser.add_argument(
        "--dual", action="store_true",
        help="Simulate two systems attached with an ethernet link")
    parser.add_argument(
        "-b", "--benchmark", action="store", type=str, dest="benchmark",
        help="Specify the benchmark to run. Available benchmarks: %s" %
        DefinedBenchmarks)

    # Metafile options
    parser.add_argument(
        "--etherdump", action="store", type=str, dest="etherdump",
        help="Specify the filename to dump a pcap capture of the"
        "ethernet traffic")

    # Disk Image Options
    parser.add_argument("--disk-image", action="append", type=str,
                        default=[], help="Path to the disk images to use.")
    parser.add_argument("--root-device", action="store", type=str,
                        default=None, help="OS device name for root partition")

    # Command line options
    parser.add_argument("--command-line", action="store", type=str,
                        default=None,
                        help="Template for the kernel command line.")
    parser.add_argument(
        "--command-line-file", action="store", default=None, type=str,
        help="File with a template for the kernel command line")
