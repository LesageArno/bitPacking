from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np
import bitarray

INT_ENCODING_SIZE = 32 #32 bits per integer

class SplitCompressor(Compressor):
    def __init__(self):
        super().__init__()

    def compress(self, arr:np.ndarray[int]) -> tuple[bitarray.bitarray,int,int]:
        """The method that compress int32 integer into smaller integers.

        Args:
            arr (np.ndarray[int]): The array of integer to compress.

        Returns:
            tuple[bitarray.bitarray,int,int]: A tuple containing in 1st position the compressed array, in 2nd the necessary bit length of the biggest element of the uncompressed array and in 3rd the length of the uncompressed array.
        """
        
        # Get the necessary bit size of the biggest element in array
        maxBitLength = self._getMaxBitLength(arr)
        
        # Compute the required size for the compressed Array and create the array
        compressedArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxBitLength+1) / INT_ENCODING_SIZE)
        compressedArr = bitarray.bitarray(np.zeros(compressedArrayLength, dtype=bool).tolist())

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

        return (compressedArr, maxBitLength, len(arr))
    
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        """The method to decompress the array compressed using this class.

        Args:
            *args (tuple[Any]): 1st index is the array, the second is the necessary bit length of the biggest element of the uncompressed array and the third of the uncompressed array.
            
        Returns:
            np.ndarray[int]: The decompressed integer array.
        """
        
        # Retrieve the variables and initialise the function variables
        compressedArr, maxBitLength, initialLength, *_ = args
        decompressedArr = []
        arrIndex = 0
        
        # Loop through the compressed array
        while True:
            
            # get the windows index to look at
            startPos = arrIndex*(maxBitLength+1)
            endPos = (arrIndex+1)*(maxBitLength+1)
            
            # Quit if out of bound or all number are uncompressed
            if endPos > len(compressedArr) or len(decompressedArr) >= initialLength:
                break
            
            # Take values
            val = compressedArr[startPos:endPos]
            
            # Otherwise, decode the element
            decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
            if val[0] == True:
                decompressedVal[0] = "-"
            
            # Update the decompressed array and continue
            decompressedArr.append(int("".join(decompressedVal), base = 2)  if decompressedVal != [] else 0)
            arrIndex += 1

        return np.array(decompressedArr)
        
    def get(self, i:int, *args:tuple[Any]) -> int:
        """Get the value at the i-th position of the compressed array.

        Args:
            i (int): The position to look at.
            *args (tuple[Any]): 1st index is the array, the second is the necessary bit length of the biggest element of the uncompressed array and in 3rd the length of the uncompressed array.


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
        val = int(representation[1:], base=2) if representation[1:] != "" else 0
        
        # Return the value and the sign
        if sign == "1":
            return -val
        return val


if __name__ == "__main__":
    arr = np.array([0])
    sC = SplitCompressor()
    
    val = sC.compress(arr)
    
    print(sC.get(0, *val), arr[0])
    print(sum(arr != sC.decompress(*val)))