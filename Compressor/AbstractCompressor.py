from abc import ABC, abstractmethod
from typing import Any
import numpy as np

class Compressor(ABC):
    @abstractmethod
    def compress(self, arr:np.ndarray[int]) -> tuple[Any]:
        """The method to be implemented/overrided for compressing the integer array

        Args:
            arr (np.ndarray[int]): An integer array to compress

        Returns:
            tuple[Any]: A tuple including at least the compressed array and the maximum bit length, it may also include an overflow area depending on the implementation.
        """
    
    @abstractmethod
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        """The method to be implemented/overrided for decompressing the array

        Args:
            *args (tuple[Any]): An input containing at least the compressed array and the maximum bit length, it may also require an overflow area depending on the implementation.

        Returns:
            np.ndarray[int]: The decompressed integer array.
        """
    
    @abstractmethod
    def get(self, args:tuple[Any]):
        """The method to find the i-th number of the compressed array.

        Args:
            *args (tuple[Any]): An input containing at least the compressed array and the maximum bit length, it may also require an overflow area depending on the implementation.
        """
    
    def _getMaxBitLength(self, arr:np.ndarray[int]) -> int:
        """Protected helper function to find the necessary bit length to encode the supremum object of the array.

        Args:
            arr (np.ndarray[int]): An array of integer

        Returns:
            int: The bit length necessary to encode the supremum object.
        """
        return int(arr.__abs__().max()).bit_length()