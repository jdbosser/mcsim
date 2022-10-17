from typing import TypeVar, Generic, Iterable, Optional
import numpy as np
from pathlib import Path
import datetime 
import pickle

SIM_DIR = "precalculated_simulations/"
MARKER_FORMAT = "%Y-%m-%d_%H-%M"

def get_marker() -> str:
    now = datetime.datetime.now()

    name = "Sim"+now.strftime(MARKER_FORMAT)

    return name

def mkdir(path):

    Path(path).mkdir(parents=True, exist_ok=True)

IteratorOutput = TypeVar("IteratorOutput")
class SavedIteratorSeq(Generic[IteratorOutput]):

    def __init__(self, iterator: Iterable[IteratorOutput], n_steps: Optional[int] = None):
    
        self.iterator = iterator
        self.n_steps = n_steps
        self.filename = None
        self.git_hash = None # To be filled in. This will garantee that 
                             # the simulation can always be run. We can
                             # checkout to the commit where this saved
                             # was created. 
    

    def is_precalculated(self) -> bool:

        if self.filename is None:
            return False
        # Check that the file exists. 
        file = Path(self.filename)
        
        return file.is_dir()


    def precalculate(self, n_steps = None):
        
        # Run super().run for n_steps, and save each time step. 
        pass  

    def _save(self, d: str, ii: int, output: IteratorOutput):
        

        print("saving step", ii)
        ar = np.array(output, dtype = object)
        np.save(d+str(ii) + ".npy", ar)
            
        # 
        # with ZipFile(self.filename, mode = "w") as zipf:
        #    compress_dir(zipf, file_base)
    
    def _save_self(self):

        mark = get_marker()
        d = SIM_DIR + mark + "/"
        mkdir(d)
        
        f = d + mark + ".pkl" 
        
        with open(f, 'wb') as fn:
            pickle.dump(self, fn, 5)

        return d
    
    def _open(self, d):
        
        for ii in range(self.n_steps):
            yield tuple(np.load(d + str(ii) + ".npy", allow_pickle = True))

    def __iter__(self):
        
        
        if self.is_precalculated():
            print("Is precalculated. Running")
            
            yield from self._open(self.filename + "/")
        # Something _open().... Something get the measurements and beamformer etc. 
        else: 
            if self.filename is None:
                mark = get_marker()
                d = SIM_DIR + mark + "/"
                mkdir(d)
                self.filename = d
        
            
            print("Is not precalculated. Running more slowly, will go faster next time. ")

            print("Saving self first")
            d = self._save_self()

            outputs = []


            # Iter and save 
            if self.n_steps is None:
                iterator = enumerate(self.iterator)                 
            else:
                iterator = zip(range(self.n_steps), self.iterator)

            for ii, output in iterator:

                self._save(d, ii, output) 
                yield output

            print("Iteration done") 

    @classmethod
    def load(cls, directory: str) -> 'SavedIteratorSeq[IteratorOutput]':
        
        # https://stackoverflow.com/questions/27732354/unable-to-load-files-using-pickle-and-multiple-modules        
        directory = SIM_DIR + directory
        dirp = Path(directory)
        
        
        if not dirp.is_dir():
            raise Exception("Doesnt seem like there is a simulation at the specified location: " + str(dirp))
        
        # Figure out how many iterations there are in the directory
        files = dirp.glob("*.npy")
        n_steps = len(list(files))
        
        pfile = list(dirp.glob("*.pkl"))[0]
        
        print("trying to open", str(pfile))
        savedsim = pickle.load(open(str(pfile), "rb"))
        savedsim.n_steps = n_steps
        savedsim.filename = directory 

        return savedsim

    
