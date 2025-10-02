import pytest
import numpy as np
import os

import main

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
    
# Benchmark file
outPath = "OUT\\benchmarkOutput.out"
with open(outPath, "w") as file:
    file.write("compressor, file, function, time\n")
    
    
    
    

# Test Split compression process
def test_splitCompression():
    for key, testVal in testFiles.items():
        split.setArr(testVal)
        split.compress()
        
        # Test get
        assert split.get(0, compressed=True) == testVal[0], f"{key}: split get index 0 different."
        assert split.get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: split get index -1 different."
        assert split.get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: split get index {((len(testVal)-1)/2).__ceil__()} different."
        
        # Test compression -> decompression pipeline
        split.decompress()
        assert np.all(split.getArr()==testVal), f"{key}: split compression process not working."
        
# Test Nosplit compression process 
def test_nosplitCompression():
    for key, testVal in testFiles.items():
        nosplit.setArr(testVal)
        nosplit.compress()
        
        # Test get
        assert nosplit.get(0, compressed=True) == testVal[0], f"{key}: nosplit get index 0 different."
        assert nosplit.get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: nosplit get index -1 different."
        assert nosplit.get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: nosplit get index {((len(testVal)-1)/2).__ceil__()} different."
        
        # Test compression -> decompression pipeline
        nosplit.decompress()
        assert np.all(nosplit.getArr()==testVal), f"{key}: nosplit compression process not working."

# Test Overflow compression process 
def test_overflowCompression():
    for overflowKey in overflow.keys(): 
        print(overflowKey)
        for key, testVal in testFiles.items():
            overflow[overflowKey].setArr(testVal)
            overflow[overflowKey].compress()
            
            # Test get
            assert overflow[overflowKey].get(0, compressed=True) == testVal[0], f"{key}: {overflowKey} get index 0 different."
            assert overflow[overflowKey].get(len(testVal)-1, compressed=True) == testVal[-1], f"{key}: {overflowKey} get index -1 different."
            assert overflow[overflowKey].get(((len(testVal)-1)/2).__ceil__(), compressed=True) == testVal[((len(testVal)-1)/2).__ceil__()], f"{key}: overflow[overflowKey] get index {((len(testVal)-1)/2).__ceil__()} different."
            
            # Test compression -> decompression pipeline
            overflow[overflowKey].decompress()
            assert np.all(overflow[overflowKey].getArr()==testVal), f"{key}: {overflowKey} compression process not working."