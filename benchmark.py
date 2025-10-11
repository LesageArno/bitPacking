import time
import numpy as np
import os

import main

# Number of test per function
REP = 10

# Create the bit packing handler
split = main.BitPacking("split")
nosplit = main.BitPacking("nosplit")
overflow = {
    "overflow1": main.BitPacking("overflow", 1),
    "overflow2": main.BitPacking("overflow", 2),
    "overflow4": main.BitPacking("overflow", 4),
    "overflow8": main.BitPacking("overflow", 8),
    "overflow12": main.BitPacking("overflow", 12)
}


# Import the test files
testFiles = {}
for file in os.listdir("IN"):
    testFiles[file.strip(".in")] = np.fromfile(f"IN\\{file}", dtype=np.int32, sep=" ")
    

# Benchmark context manager  
class BenchmarkContext():
    def __init__(self, outPath:str, createFile:bool, **kwargs):
        self.outPath = outPath
        self.kwargs = kwargs
        self.file = None
        self.createFile = createFile
        
    def __enter__(self):
        if self.createFile:
            self.file = open(self.outPath, "w")
            for key, value in self.kwargs.items():
                self.file.write(f'"{key}", ')
            self.file.write('"time"\n')
        else:
            self.file = open(self.outPath, "a")
        self.timeBegin = time.time()
    
    def __exit__(self, *args):
        elapsedTime = time.time()-self.timeBegin
        if not all(i is None for i in self.kwargs.values()):
            for key, value in self.kwargs.items():
                self.file.write(f'"{value}", ')
            self.file.write(f"{elapsedTime}\n")
        self.file.close()


# Function to benchmark flow
def proceedBenchmark(compressor:main.BitPacking, out:str = "OUT\\benchmark.out"):
    with BenchmarkContext(outPath=out, createFile=True, benchID=None, inFile=None, func=None):
        pass
    
    count = 0
    for key, value in testFiles.items():
        for _ in range(REP):
            print(f"step [{key}]: {(count//4)%REP}/{REP}")
            compressor.setArr(value)

            with BenchmarkContext(outPath=out, createFile=False, benchID=count, inFile=key, func="transmitRaw"):
                compressor.transmit(compressed=False)
            
            count+=1
            with BenchmarkContext(outPath=out, createFile=False, benchID=count, inFile=key, func="compress"):
                compressor.compress()
            
            count+=1
            with BenchmarkContext(outPath=out, createFile=False, benchID=count, inFile=key, func="transmit"):
                compressor.transmit(compressed=True)
                
            count+=1
            with BenchmarkContext(outPath=out, createFile=False, benchID=count, inFile=key, func="decompress"):
                compressor.decompress()
            count+=1


# Proceed Benchmark
proceedBenchmark(split, "OUT\\splitBenchmark.out")
proceedBenchmark(nosplit, "OUT\\nosplitBenchmark.out")
for key, value in overflow.items():
    proceedBenchmark(value, f"OUT\\{key}Benchmark.out")