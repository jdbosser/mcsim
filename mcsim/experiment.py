from typing import TypeVar, Generic, Protocol, Callable
import numpy as np
from pathlib import Path
from pytimedinput import timedKey # type: ignore
import sys
import datetime
from dataclasses import dataclass
import argparse
from git.repo import Repo # type: ignore

MARKER_FORMAT = "%Y-%m-%d_%H-%M"
def get_marker(s) -> str:
    now = datetime.datetime.now()

    name = s+now.strftime(MARKER_FORMAT)

    return name

def query_yes_no(question, default="yes") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def query_yes_no_timed(default = False, time = 5) -> bool:

    defalt = "y" if default else "n"

    userText, timedOut = timedKey(
        "Press y or n, default is %s. Continuing in %d seconds..." % (defalt, time), 
        allowCharacters="yn",
        timeout = time
    )
    if timedOut:
        return default
    if userText.lower() == "y":
        return True
    else:
        return False

def mkdir(path):

    Path(path).mkdir(parents=True, exist_ok=True)


CACHE_DIR = Path("experiments/experiments_cache")

Result = TypeVar("Result")

class SaveableExperiment(Generic[Result], Protocol):
    
    name: str
    @property
    def run(self) -> Callable[[], Result]: 
        ...

    @property
    def plot(self) -> Callable[[Result], None]:
        ...

FilterName = str
MetricName = str
FilterResults = dict[MetricName, np.ndarray]
TRes = dict[FilterName, FilterResults]

def runExperiment(exp: SaveableExperiment[TRes], plot: bool = True, only_plot = False, latest = False):
    
    # Check that there are no runs with the experiment already, 
    # Ask to overwrite if wished to do so. 

    # Check if there is already an experiment in the experiment cache, with the same name
    prevRuns = list(CACHE_DIR.glob(exp.name + "*"))

    shouldRun = False 
    
    def query_user():
        return query_yes_no("A run for this experiment already exist. Do you want to recalculate?", default = "no") 

    shouldRun = False or (not plot) or (not prevRuns) and (not only_plot) or (query_user())

    if shouldRun:
        results: object = exp.run()
        results_arr = np.array(results)
        p = CACHE_DIR / (get_marker(exp.name))
        mkdir(p)

        for filt_name, data in results.items():

            filename = p / (filt_name + ".npz") 

            np.savez(filename, **data)
    else:
        results = loadExperiment(exp.name, latest)

    
    # Plot the results
    if plot or only_plot:
        exp.plot(results)

def loadExperiment(experiment_name: str, load_latest = False) -> np.ndarray:

    prevRuns = list(CACHE_DIR.glob(experiment_name + "*"))
    if not prevRuns:
        raise Exception(
            "No previous runs with the experiment with the name: " + experiment_name
        )

    sorted_prevruns = sorted((str(p) for p in prevRuns), reverse = True)
    if not load_latest:
        print("Select a run to plot")
        terminal_menu = TerminalMenu(sorted_prevruns)
        last_run = terminal_menu.show()
        selected_run = sorted_prevruns[last_run]
    else:
        selected_run = sorted((str(p) for p in prevRuns), reverse = True)[0]


    print("You selected", selected_run)
    # List the directory
    p = Path(selected_run)
    files = p.iterdir()
    return {fname.stem: np.load(fname, mmap_mode = "r") for fname in files}

@dataclass
class Experiment(Generic[Result]):
    name: str
    run: Callable[[], Result]
    plot: Callable[[Result], None]

def get_args(description):


    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--no-plot", help = "do not plot the results of the experiment", action = "store_false")
    parser.add_argument("--only-plot", help = "only plot the results of the experiment", action = "store_true")
    parser.add_argument("--latest", help = "select the latest experiment", action = "store_true")
    
    return parser.parse_args()

def experimentCLI(exp: Experiment, description: str):

    args = get_args(description)

    runExperiment(exp, args.no_plot, args.only_plot, args.latest)

def git_head() -> str:
    repo = Repo(search_parent_directories=True)
    head = repo.head.object
    return head.hexsha

"""
    TODO: Add ability to save the git commit for when the results were run
    
    some_results["GIT_COMMIT"] = np.array(git_head())
    
    TODO: add ability to save numpy random seed, for reproducibility

    seed = np.random.SeedSequence().entropy
    rng = np.random.default_rng(seed)

    TODO: add ability to abort simulation/experiment and continue it. Difficult. 

"""
