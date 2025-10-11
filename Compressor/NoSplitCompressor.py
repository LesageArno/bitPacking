from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np
import bitarray

INT_ENCODING_SIZE = 32 #32 bits per integer

class NoSplitCompressor(Compressor):
    def __init__(self):
        super().__init__()

    def compress(self, arr:np.ndarray[int]) -> tuple[bitarray.bitarray, bitarray.bitarray,int,int]:
        """The method that compress int32 integer into smaller integers.

        Args:
            arr (np.ndarray[int]): The array of integer to compress

        Returns:
            tuple[bitarray.bitarray, bitarray.bitarray,int,int]: A tuple containing in 1st position the compressed array, in 2nd position an array containing the signs, in 3rd the necessary bit length of the biggest element of the uncompressed array, and in 4th the length of the uncompressed array.
        """
        # Get the necessary bit size of the biggest element in array
        maxBitLength = max(self._getMaxBitLength(arr), 1)
        
        # Compute the maximum capacity of a compressed integer and the index for which we need to move on the next int32
        intCompressedCapacity = (INT_ENCODING_SIZE/maxBitLength).__floor__()
        criticalIndex = intCompressedCapacity * maxBitLength
        
        # Intialise the compressed array
        compressedArrayLength = INT_ENCODING_SIZE*(len(arr)/intCompressedCapacity).__ceil__()
        compressedArr = bitarray.bitarray(np.zeros(compressedArrayLength, dtype=bool).tolist())
        
        signArr = bitarray.bitarray(np.zeros(len(arr), dtype=bool).tolist())

        # Compute the row necessary shift of position when moving on the next int32 
        criticalShift = INT_ENCODING_SIZE - intCompressedCapacity * maxBitLength
        intNo = 0
        
        # Compress the integer array into the boolean array
        for arrIndex, elem in enumerate(arr):    
            # Get the bit representation of an integer, ex:  -12 -> '-0001100'
            bitVal = format(elem, "08b")
            
            # Get the index to place the boolean
            pos = arrIndex * maxBitLength + intNo*criticalShift
            
            # If the position is bigger than the critical index, then move on the next int32 and update position
            if (pos >= criticalIndex*(intNo+1) + criticalShift*intNo):
                intNo += 1
                pos += criticalShift

            # Manage the sign of the entry
            if bitVal.startswith("-"):
                signArr[arrIndex] = True
            else:
                signArr[arrIndex] = False
                    
            # Correct the length of bits to maxBitLength
            correctedBitVal = bitVal[-maxBitLength:].strip("-")
            correctedBitVal = "0" * (maxBitLength-len(correctedBitVal)) + correctedBitVal
                    
            # For each bit, register it at the right place of the array.
            for bitIndex, bitElem in enumerate(correctedBitVal[-maxBitLength:]):
                compressedArr[pos+bitIndex] = True if bitElem == "1" else False

        return (compressedArr, signArr, maxBitLength, len(arr))
    
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        """The method to decompress the array compressed using this class.

        Args:
            *args (tuple[Any]): A tuple containing in 1st position the compressed array, in 2nd position an array containing the signs, in 3rd the necessary bit length of the biggest element of the uncompressed array, and in 4th the length of the uncompressed array.
            
        Returns:
            np.ndarray[int]: The decompressed integer array.
        """
        
        # Retrive and compute necessary information
        compressedArr, signArr, maxBitLength, initialLength, *_ = args

        # Apply get repeatidely
        return np.array([self.get(i, *args) for i in range(initialLength)])
        
    def get(self, i:int, *args:tuple[Any]) -> int:
        """Get the value at the i-th position of the compressed array.

        Args:
            i (int): The position to look at.
            *args (tuple[Any]): A tuple containing in 1st position the compressed array, in 2nd position an array containing the signs, in 3rd the necessary bit length of the biggest element of the uncompressed array, and in 4th the length of the uncompressed array.

        Returns:
            int: The value of the i-th position.
        """
        
        # Retrieve the variables and compute the cell to look at
        compressedArr, signArr, maxBitLength, *_ = args
        intCompressedCapacity = (INT_ENCODING_SIZE/maxBitLength).__floor__()
        
        # Compute the position to check (taking into account the int32 cutting)
        if intCompressedCapacity != 1:
            lookAt = (maxBitLength * (i%intCompressedCapacity)) + ((i//intCompressedCapacity) * INT_ENCODING_SIZE)
        else:
            lookAt = i * INT_ENCODING_SIZE
                
        # Retrieve the necessary cells
        num = compressedArr[lookAt:lookAt+maxBitLength]
        
        # Convert the number into base 10
        representation = "".join(["0" if i == False else "1" for i in num])
        val = int(representation, base=2)
        
        # Return the value and the sign
        if signArr[i] == True:
            return -val
        return val


if __name__ == "__main__":
    arr = np.random.randint(-2**16+1, 2**16-1, 100_000)
    nsC = NoSplitCompressor()
    
    val = nsC.compress(arr)
    print(nsC.get(len(arr)-1, *val), arr[-1])
    print(nsC.get(len(arr)-2, *val), arr[-2])
    print(nsC.get(0, *val), arr[0])
    print(nsC.get(87333, *val), arr[87333])
    
    print(np.all(arr == nsC.decompress(*val)))