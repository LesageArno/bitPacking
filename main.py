from Compressor.AbstractCompressor import Compressor
from Compressor.SplitCompressor import SplitCompressor
from Compressor.NoSplitCompressor import NoSplitCompressor
from Compressor.OverflowCompressor import OverflowCompressor

from typing import Literal, Any
import numpy as np


def createCompressor(mode:Literal["nosplit","split","overflow"]) -> Compressor:
    return {
        "nosplit": NoSplitCompressor,
        "split": SplitCompressor,
        "overflow": OverflowCompressor
    }[mode]()


class BitPacking:
    def __init__(self, mode:Literal["nosplit","split","overflow"]):
        self.compressor:Compressor = createCompressor(mode)
        self.arr:np.ndarray[int]
        self.compressed:tuple[Any]

    def getArr(self) -> np.ndarray[int]:
        return self.arr
    
    def getCompressedArr(self) -> tuple[Any]:
        return self.compressed
    
    def setArr(self, arr:np.ndarray[int]) -> None:
        self.arr = arr
    
    def compress(self) -> None:
        self.compressed = self.compressor.compress(self.arr)
    
    def decompress(self) -> None:
        self.arr = self.compressor.decompress(*self.compressed)

    def get(self, i:int) -> None:
        if not self.compressed:
            return self.arr[i]
        return self.compressor.get(i, *self.compressed)



if __name__ == "__main__":
    a:list[int] = list(range(21))
    bp = BitPacking("split")
    bp.setArr(a)
    bp.compress()