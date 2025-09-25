from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np

INT_ENCODING_SIZE = 32 #32 bits per integer

class SplitCompressor(Compressor):
    def __init__(self):
        super().__init__()

    def compress(self, arr:np.ndarray[int]) -> tuple[np.ma.MaskedArray[bool],int]:

        # Get the necessary bit size of the biggest element in array
        maxBitLength = self._getMaxBitLength(arr)
        
        # Compute the required size for the compressed Array and create the array
        compressedArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxBitLength+1) / INT_ENCODING_SIZE)
        compressedArr = np.ma.MaskedArray(np.zeros(compressedArrayLength, dtype=bool), mask=True)

        # Compress the integer array into the boolean array
        for arrIndex, elem in enumerate(arr):
            
            # Get the bit representation of an integer, ex:  -12 -> '-0001100'
            bitVal = format(elem, "08b")
            
            # Register the polarity of the integer on the first bit. So -5 is encoded as: 1101 where 1 is the sign and 101 the number  
            if bitVal.startswith("-"):
                compressedArr[arrIndex*(maxBitLength+1)] = True
            else:
                compressedArr[arrIndex*(maxBitLength+1)] = False
            
            # Correct the length of bits to maxBitLength
            correctedBitVal = bitVal[-maxBitLength:].strip("-")
            correctedBitVal = "0"*(maxBitLength-len(correctedBitVal))+correctedBitVal
            
            # For each bit, register it at the right place of the array.
            for bitIndex, bitElem in enumerate(correctedBitVal[-maxBitLength:]):
                compressedArr[arrIndex*(maxBitLength+1)+bitIndex+1] = True if bitElem == "1" else False

        return (compressedArr, maxBitLength)
    
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        """The method to be implemented/overrided for decompressing the array

        Args:
            *args (tuple[Any]): 1st index is the array and the second is the necessary bit length of the biggest element of the uncompressed array.
            
        Returns:
            np.ndarray[int]: The decompressed integer array.
        """
        
        # Retrieve the variables and initialise the function variables
        compressedArr, maxBitLength, *_ = args
        decompressedArr = []
        count = 0
        
        # Loop through the compressed array
        while True:
            # Avoid OutOfBound error
            if (count+1)*(maxBitLength+1) > len(compressedArr):
                break
            
            # If all number are decompressed then quit
            val = compressedArr[count*(maxBitLength+1):(count+1)*(maxBitLength+1)]
            if val[0] is np.ma.masked:
                break
            
            # Otherwise, decode the element
            decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
            if val[0] == True:
                decompressedVal[0] = "-"
            
            # Update the decompressed array and continue
            decompressedArr.append(int("".join(decompressedVal), base = 2))
            count += 1

        return np.array(decompressedArr, dtype=int)
        
    def get(self, i:int, *args:tuple[Any]) -> int:
        """Get the value at the i-th position of the compressed array.

        Args:
            i (int): The position to look at.
            *args (tuple[Any]): 1st index is the array and the second is the necessary bit length of the biggest element of the uncompressed array.


        Returns:
            int: The value of the i-th position.
        """
        # Retrieve the variables and compute the cell to look at
        compressedArr, maxBitLength, *_ = args
        lookAt = (maxBitLength+1)*i
        
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
    sC = SplitCompressor()
    
    val = sC.compress(arr_SmallInt)
    sum(arr_SmallInt != sC.decompress(*val))