from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np

INT_ENCODING_SIZE = 32 #32 bits per integer

class NoSplitCompressor(Compressor):
    def __init__(self):
        super().__init__()

    def compress(self, arr:np.ndarray[int]) -> tuple[np.ndarray[bool],int,int,int]:
        """The method that compress int32 integer into smaller integers.

        Args:
            arr (np.ndarray[int]): The array of integer to compress

        Returns:
            tuple[np.ndarray[bool],int,int,int]: A tuple containing in 1st position the compressed array, in 2nd the necessary bit length of the biggest element of the uncompressed array, in 3rd the index for which we need to move on next compressed integer, and in 4th the length of the uncompressed array.
        """
        # Get the necessary bit size of the biggest element in array
        maxBitLength = self._getMaxBitLength(arr)
        
        # Compute the maximum capacity of a compressed integer and the index for which we need to move on the next int32
        intCompressedCapacity = (INT_ENCODING_SIZE/(maxBitLength+1)).__floor__()
        criticalIndex = intCompressedCapacity * (maxBitLength+1)
        
        # Intialise the compressed array
        compressedArrayLength = INT_ENCODING_SIZE*(len(arr)/intCompressedCapacity).__ceil__()
        compressedArr = np.zeros(compressedArrayLength, dtype=bool)

        # Compute the row necessary shift of position when moving on the next int32 
        criticalShift = INT_ENCODING_SIZE - intCompressedCapacity * (maxBitLength+1)
        intNo = 0
        
        # Compress the integer array into the boolean array
        for arrIndex, elem in enumerate(arr):    
            # Get the bit representation of an integer, ex:  -12 -> '-0001100'
            bitVal = format(elem, "08b")
            
            # Get the index to place the boolean (including potential shift)
            pos = arrIndex * (maxBitLength+1) + intNo*criticalShift
            
            # If the position (including potential shift) is bigger than the critical index (including potential shift), then move on the next int32 and update position
            if (pos >= criticalIndex*(intNo+1) + criticalShift*intNo):
                intNo += 1
                pos += criticalShift

            # Manage the sign of the entry
            if bitVal.startswith("-"):
                compressedArr[pos] = True
            else:
                compressedArr[pos] = False
                    
            # Correct the length of bits to maxBitLength
            correctedBitVal = bitVal[-maxBitLength:].strip("-")
            correctedBitVal = "0" * (maxBitLength-len(correctedBitVal)) + correctedBitVal
                    
            # For each bit, register it at the right place of the array.
            for bitIndex, bitElem in enumerate(correctedBitVal[-maxBitLength:]):
                compressedArr[pos+bitIndex+1] = True if bitElem == "1" else False

        return (compressedArr, maxBitLength, criticalIndex, len(arr))
    
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        """The method to decompress the array compressed using this class.

        Args:
            *args (tuple[Any]): 1st index is the array, the second is the necessary bit length of the biggest element of the uncompressed array, the third is the critical index and the fourth the length of the uncompressed array 
            
        Returns:
            np.ndarray[int]: The decompressed integer array.
        """
        
        # Retrive and compute necessary information
        compressedArr, maxBitLength, criticalIndex, initialLength, *_ = args
        intCompressedCapacity = (INT_ENCODING_SIZE/(maxBitLength+1)).__floor__()
        criticalShift = INT_ENCODING_SIZE - intCompressedCapacity * (maxBitLength+1)
        
        # Initialise variable for the loop
        decompressedArr = []
        arrIndex = 0
        intNo = 0

        # Loop through the compressed array
        while True:
            
            # get the windows index to look at
            endPos = (arrIndex+1)*(maxBitLength+1) + intNo*criticalShift
            startPos = arrIndex*(maxBitLength+1) + intNo*criticalShift
            
            # Update the starting and ending position whenever critical shift are involved
            if (startPos >= criticalIndex*(intNo+1) + criticalShift*intNo):
                intNo += 1
                startPos += criticalShift
                endPos += criticalShift
            
            # Quit if out of bound or all number are uncompressed
            if endPos > len(compressedArr) or len(decompressedArr) >= initialLength:
                break
                    
            # Retrieve the value
            val = compressedArr[startPos:endPos]
                    
            # and decode...
            decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
            if val[0] == True:
                decompressedVal[0] = "-"
                    
            # Update the decompressed array and continue
            decompressedArr.append(int("".join(decompressedVal), base = 2))
            arrIndex += 1


        return np.array(decompressedArr, dtype=int)
        
    def get(self, i:int, *args:tuple[Any]) -> int:
        """Get the value at the i-th position of the compressed array.

        Args:
            i (int): The position to look at.
            *args (tuple[Any]): A tuple containing in 1st position the compressed array, in 2nd the necessary bit length of the biggest element of the uncompressed array, in 3rd the index for which we need to move on next compressed integer, and in 4th the length of the uncompressed array.

        Returns:
            int: The value of the i-th position.
        """
        
        # Retrieve the variables and compute the cell to look at
        compressedArr, maxBitLength, *_ = args
        intCompressedCapacity = (INT_ENCODING_SIZE/(maxBitLength+1)).__floor__()
        
        # Compute the position to check (taking into account the int32 cutting)
        lookAt = ((maxBitLength+1) * (i%intCompressedCapacity)) + ((i//intCompressedCapacity) * INT_ENCODING_SIZE)
                
        # Retrieve the necessary cells
        if lookAt + maxBitLength >= len(compressedArr)-1:
            num = compressedArr[lookAt:]
        else:
            num = compressedArr[lookAt:lookAt+maxBitLength+1]
        
        # Convert the number into base 10
        representation = "".join(["0" if i == False else "1" for i in num])
        sign = representation[0]
        val = int(representation[1:], base=2)
        
        # Return the value and the sign
        if sign == "1":
            return -val
        return val


if __name__ == "__main__":
    arr_SmallInt = np.random.randint(-2**8+1, 2**8, 100_000)
    nsC = NoSplitCompressor()
    
    val = nsC.compress(arr_SmallInt)
    
    sum(arr_SmallInt != nsC.decompress(*val))