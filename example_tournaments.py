
"""
Runs example tournaments using the Axelrod library available at
https://github.com/marcharper/Axelrod
"""

import argparse
import multiprocessing
import os
import sys

import axelrod


def ensure_directory(directory):
    """Makes sure that a directory exists and creates it if it does not."""

    head, tail = os.path.split(directory)
    if head:
        ensure_directory(head)

    if not os.path.isdir(directory):
        os.mkdir(directory)

def axelrod_strategies(cheaters=False, meta=False):
    """Obtains the list of strategies from Axelrod library."""

    s = []
    s.extend(axelrod.basic_strategies)
    s.extend(axelrod.ordinary_strategies)
    if cheaters:
        s.extend(axelrod.cheating_strategies)
    if not meta:
        s = [t for t in s if not t.__name__.startswith("Meta")]
    # Instantiate
    s = [t() for t in s]
    # Sort by name
    s.sort(key=str)
    return s

def classic_strategies():

    strategies = [
        axelrod.Cooperator(),
        axelrod.Defector(),
        axelrod.GTFT(),
        axelrod.Grudger(),
        axelrod.Random(),
        axelrod.TitForTat(),
        axelrod.TitFor2Tats(),
        axelrod.WinStayLoseShift(),
    ]
    return strategies

def finite_memory_strategies(lower=0, upper=float('inf')):
    """Filter strategies down to those that have finite memory_depth."""

    strategies = []
    for s in axelrod_strategies():
        if s.memory_depth >= lower and s.memory_depth < upper:
            strategies.append(s)
    return strategies

def memoryone_strategies():
    """Filter strategies down to those that are memoryone, that is having
    memory_depth 0 or 1."""

    return finite_memory_strategies(lower=0, upper=2)

def first_axelrod_strategies():
    """
    The strategies in Axelrod's first tournament.
    Warning: Incomplete!
    """

    strategies = [
        axelrod.TitForTat(),
        axelrod.Grofman(),
        axelrod.Shubik(),
        axelrod.Grudger(),
        axelrod.Davis(),
        axelrod.Joss(),
        axelrod.Tullock()
    ]
    return strategies

def tscizzle_strategies():
    """The list of strategies used in @tscizzle's Morality Metrics paper."""

    strategies = [
        axelrod.Cooperator(),
        axelrod.Defector(),
        axelrod.Eatherley(),
        axelrod.Champion(),
        axelrod.GTFT(p=0.1),
        axelrod.GTFT(p=0.3),
        axelrod.GoByMajority(soft=True),
        axelrod.GoByMajority(soft=False),
        axelrod.TitFor2Tats(),
        axelrod.Random(0.8),
        axelrod.Random(0.5),
        axelrod.Random(0.2),
        axelrod.WinStayLoseShift(), # Pavlov
        axelrod.TitForTat(),
        axelrod.TwoTitsForTat(),
        axelrod.Grudger(), # Friedman
        axelrod.Tester(),
        axelrod.SuspiciousTitForTat(),
        axelrod.Joss(0.1),
        axelrod.Joss(0.3),
    ]
    return strategies

def sp_strategies():
    """The list of strategies used in Stewart and Plotkin's 2012 tournament."""

    strategies = [
        axelrod.Cooperator(), # ALLC
        axelrod.Defector(), # ALLD
        axelrod.GTFT(),
        axelrod.GoByMajority(soft=False), # HARD_MAJO
        #axelrod.GoByMajority(soft=True), # SOFT_MAJO
        axelrod.TitFor2Tats(), # TFT2
        axelrod.HardTitFor2Tats(), # HARD_TFT2
        axelrod.Random(), # RANDOM
        axelrod.WinStayLoseShift(), # WSLS
        axelrod.TitForTat(),
        axelrod.HardTitForTat(), # HARD_TFT
        axelrod.Grudger(), # GRIM
        axelrod.Joss(), # HARD_JOSS
        axelrod.ZDGTFT2(),
        axelrod.ZDExtort2(),
        axelrod.Prober(),
        axelrod.Prober2(),
        axelrod.Prober3(),
        axelrod.HardProber(),
        axelrod.Calculator(),
    ]
    return strategies

def run_tournament(name, strategies, repetitions=100, with_ecological=False,
               processes=None, rebuild_cache=True, noise=0, turns=200):
    if not processes:
        # Use them all!
        processes = multiprocessing.cpu_count()

    # Make sure the output directories exist
    root_directory = os.path.join("assets", "tournaments")
    output_directory = os.path.join(root_directory, name)
    ensure_directory(output_directory)

    # Set up a tournament manager
    tm = axelrod.TournamentManager(output_directory=output_directory,
                                   with_ecological=with_ecological,
                                   save_cache=rebuild_cache)
    tm.add_tournament(name, strategies, repetitions=repetitions, turns=turns,
                      processes=processes, noise=noise)
    # Run the tournaments
    tm.run_tournaments()
    results = tm._tournaments[0].result_set
    return results

def parse_args():
    parser = argparse.ArgumentParser(description="Run Sample Axelrod tournaments")

    parser.add_argument(
        '-t',
        '--turns',
        type=int,
        default=200,
        help='turns per pair')

    parser.add_argument(
        '-r', '--repetitions',
        type=int,
        default=10,
        help='round-robin repetitions')

    parser.add_argument(
        '-p', '--processes',
        type=int,
        default=None,
        help='Number of parallel processes to spawn. 0 uses cpu count.')

    parser.add_argument(
        '-n', '--noise',
        type=float,
        default=0,
        help='Noise level')

    parser.add_argument(
        '-a',
        "--all_strategies",
        action='store_true',
        dest="all_strategies",
        help='Run just the all strategies tournament')

    args = parser.parse_args()

    return (args.turns, args.repetitions, args.processes, args.noise,
            args.all_strategies)


if __name__ == "__main__":
    turns, repetitions, processes, noise, all_strategies = parse_args()

    if all_strategies:
        strategies_names = [(axelrod_strategies(cheaters=False), "AllFairStrategies")]
    else:
        strategies_names = [
            (memoryone_strategies(), "Memoryone"),
            (finite_memory_strategies(), "FiniteMemory"),
            (tscizzle_strategies(), "tscizzle"),
            (sp_strategies(), "StewartPlotkin2012") ]
    for strategies, name in strategies_names:
        if noise:
            name += "-noise"
        run_tournament(name, strategies, repetitions=repetitions, turns=turns, noise=noise, processes=processes)
