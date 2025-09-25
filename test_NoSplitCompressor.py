import pytest
from Compressor.NoSplitCompressor import NoSplitCompressor
import numpy as np


arr_SmallInt = np.random.randint(-2**8+1, 2**8, 100_000)
arr_LargeInt = np.random.randint(-2**16+1, 2**16, 100_000)

nsC = NoSplitCompressor()
compressed_SmallInt = nsC.compress(arr_SmallInt)
compressed_LargeInt = nsC.compress(arr_LargeInt)


# Small Int compression process
def test_compression_smallInt():
    assert np.all(nsC.decompress(*compressed_SmallInt) == arr_SmallInt)

# Large Int compression process
def test_compression_largeInt():
    assert np.all(nsC.decompress(*compressed_LargeInt) == arr_LargeInt)

# Test to get first element
def test_get0():
    assert arr_SmallInt[0] == nsC.get(0, *compressed_SmallInt)
    assert arr_LargeInt[0] == nsC.get(0, *compressed_LargeInt)

# Test to get Middle element
def test_getMiddle():
    assert arr_SmallInt[56804] == nsC.get(56804, *compressed_SmallInt)
    assert arr_LargeInt[56804] == nsC.get(56804, *compressed_LargeInt)

# Test to get last element
def test_getLast():
    assert arr_SmallInt[-1] == nsC.get(99_999, *compressed_SmallInt)
    assert arr_LargeInt[-1] == nsC.get(99_999, *compressed_LargeInt)