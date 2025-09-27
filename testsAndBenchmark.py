import pytest
import numpy as np
import os
import time

import main

# Create the bit packing handler
split = main.BitPacking("split")
nosplit = main.BitPacking("nosplit")
overflow = main.BitPacking("overflow")

# Import the test files
testFiles = {}
for file in os.listdir("IN"):
    testFiles[file.strip(".in")] = np.fromfile(f"IN\\{file}", dtype=np.int32, sep=" ")
    
# Benchmark file
outPath = "OUT\\benchmarkOutput.out"
with open(outPath, "w") as file:
    file.write("compressor, file, function, time\n")
  
# Benchmark context manager  
class BenchmarkContext():
    def __init__(self, outPath:str, inFile:str, testedFunction:str, compressor:str):
        self.outPath = outPath
        self.inFile = inFile
        self.testedFunction = testedFunction
        self.compressor = compressor
        self.file = None
    
    def __enter__(self):
        self.file = open(self.outPath, "a")
        self.timeBegin = time.time()
    
    def __exit__(self, *args):
        self.file.write(f'"{self.compressor}", "{self.inFile}", "{self.testedFunction}", {time.time()-self.timeBegin}\n')
        self.file.close()

    
# Test Split compression process
def test_splitCompression():
    for key, testVal in testFiles.items():
        split.setArr(testVal)
        
        # Benchmark compress
        with BenchmarkContext(outPath, key, "compress", "split"):
            split.compress()
        
        # Test get
        assert split.get(0, compressed=True) == testVal[0], f"{key}: split get index 0 different."
        assert split.get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: split get index -1 different."
        assert split.get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: split get index {((len(testVal)-1)/2).__ceil__()} different."
        
        # Test and benchmark compression -> decompression pipeline
        with BenchmarkContext(outPath, key, "decompress", "split"):
            split.decompress()
        assert np.all(split.getArr()==testVal), f"{key}: split compression process not working."
        
        # Benchmark transmission
        with BenchmarkContext(outPath, key, "transmitCompressed", "split"):
            split.transmit()
        with BenchmarkContext(outPath, key, "transmitDecompressed", "split"):
            split.transmit(False)

# Test Nosplit compression process 
def test_nosplitCompression():
    for key, testVal in testFiles.items():
        nosplit.setArr(testVal)
        
        # Benchmark compress
        with BenchmarkContext(outPath, key, "compress", "nosplit"):
            nosplit.compress()
        
        # Test get
        assert nosplit.get(0, compressed=True) == testVal[0], f"{key}: nosplit get index 0 different."
        assert nosplit.get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: nosplit get index -1 different."
        assert nosplit.get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: nosplit get index {((len(testVal)-1)/2).__ceil__()} different."
        
        # Test and benchmark compression -> decompression pipeline
        with BenchmarkContext(outPath, key, "decompress", "nosplit"):
            nosplit.decompress()
        assert np.all(nosplit.getArr()==testVal), f"{key}: nosplit compression process not working."
        
        # Benchmark transmission
        with BenchmarkContext(outPath, key, "transmitCompressed", "nosplit"):
            nosplit.transmit()
        with BenchmarkContext(outPath, key, "transmitDecompressed", "nosplit"):
            nosplit.transmit(False)

# Test Overflow compression process 
def test_overflowCompression():
    for key, testVal in testFiles.items():
        overflow.setArr(testVal)
        
        # Benchmark compress
        with BenchmarkContext(outPath, key, "compress", "overflow"):
            overflow.compress()
        
        # Test get
        assert overflow.get(0, compressed=True) == testVal[0], f"{key}: overflow get index 0 different."
        assert overflow.get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: overflow get index -1 different."
        assert overflow.get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: overflow get index {((len(testVal)-1)/2).__ceil__()} different."
        
        # Test and benchmark compression -> decompression pipeline
        with BenchmarkContext(outPath, key, "decompress", "overflow"):
            overflow.decompress()
        assert np.all(overflow.getArr()==testVal), f"{key}: overflow compression process not working."
        
        # Benchmark transmission
        with BenchmarkContext(outPath, key, "transmitCompressed", "overflow"):
            overflow.transmit()
        with BenchmarkContext(outPath, key, "transmitDecompressed", "overflow"):
            overflow.transmit(False)