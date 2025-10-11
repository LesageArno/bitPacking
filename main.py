from Compressor.AbstractCompressor import Compressor
from Compressor.SplitCompressor import SplitCompressor
from Compressor.NoSplitCompressor import NoSplitCompressor
from Compressor.OverflowCompressor import OverflowCompressor

from typing import Literal, Any
import numpy as np

import pickle
import io


def createCompressor(mode:Literal["nosplit","split","overflow"], *args) -> Compressor:
    return {
        "nosplit": NoSplitCompressor,
        "split": SplitCompressor,
        "overflow": OverflowCompressor
    }[mode](*args)


class BitPacking:
    def __init__(self, mode:Literal["nosplit","split","overflow"], *args):
        self.__compressor:Compressor = createCompressor(mode, *args)
        self.__arr:np.ndarray[int]
        self.__compressed:tuple[Any]

    def getArr(self) -> np.ndarray[int]:
        return self.__arr
    
    def getCompressedArr(self) -> tuple[Any]:
        return self.__compressed
    
    def setArr(self, arr:np.ndarray[int]) -> None:
        self.__arr = arr
    
    def compress(self) -> None:
        self.__compressed = self.__compressor.compress(self.__arr)
    
    def decompress(self) -> None:
        self.__arr = self.__compressor.decompress(*self.__compressed)

    def get(self, i:int, compressed:bool=False) -> int:
        if not compressed:
            return self.__arr[i]
        return self.__compressor.get(i, *self.__compressed)
    
    def transmit(self, compressed:bool = True) -> None:
        # Simulate communication
        ## Serialisation
        compressed_bytes = pickle.dumps(self.__compressed if compressed else self.__arr)
        buf = io.BytesIO()
        
        # Send
        buf.write(compressed_bytes)
        
        # Read
        buf.seek(0)
        buf.read()

    def changeMode(self, mode:Literal["nosplit","split","overflow"]) -> None:
        self.__compressor = createCompressor(mode)
        self.__compressed = None

if __name__ == "__main__":
    ...