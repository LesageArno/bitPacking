from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np
import bitarray

INT_ENCODING_SIZE = 32 #32 bits per integer

class OverflowCompressor(Compressor):
    def __init__(self, threshold:int = 12):
        super().__init__()
        self.threshold = max(1,threshold)
        
    def compress(self, arr:np.ndarray[int]) -> tuple[bitarray.bitarray,int,bitarray.bitarray,int,int]:
        
        # Just rename threshold for safety
        overflowThresholdBitLength = self.threshold
        
        # Compute the max bit length of the supremum element in the overflow area and outside
        try:
            maxOverflowBitLength = int(arr[arr.__abs__() >= 2**overflowThresholdBitLength].__abs__().max()).bit_length()
        except ValueError:
            maxOverflowBitLength = 0
        try:
            maxBitLength = int(arr[arr.__abs__() < 2**overflowThresholdBitLength].__abs__().max()).bit_length()
        except ValueError:
            maxBitLength = 0

        # Compute the length of the areas and create the compressed and overflow array
        compressedArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxBitLength+2) / INT_ENCODING_SIZE)
        overflowArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxOverflowBitLength+1) / INT_ENCODING_SIZE)
        compressedArr = bitarray.bitarray(np.zeros(compressedArrayLength, dtype=bool).tolist())
        overflowArr = bitarray.bitarray(np.zeros(overflowArrayLength, dtype=bool).tolist())

        # Initialise the necessary shift in position depending on the number of overflowed integer 
        overflowCount = 0
        
        # Compress the array
        for arrIndex, elem in enumerate(arr):
            # Get the bit representation of an integer, ex:  -12 -> '-0001100'
            bitVal = format(elem, "08b")
            
            # Compute the position to set the value
            startPos = arrIndex*(maxBitLength+2) - overflowCount*(maxBitLength+1)
            
            # If the element is in the overflow area
            if abs(elem) >= 2**maxBitLength:
                
                # Indicate it in the compressedArray and compute the corresponding position within the overflow area
                compressedArr[startPos] = True                
                overflowStartPos = overflowCount * (maxOverflowBitLength+1)
                
                # Add the sign bit in the overflow
                overflowArr[overflowStartPos] = True if bitVal.startswith("-") else False
                
                # Correct the length of bits to maxOverflowBitLength
                correctedBitVal = bitVal[-maxOverflowBitLength:].strip("-")
                correctedBitVal = "0"*(maxOverflowBitLength-len(correctedBitVal))+correctedBitVal
                
                # Place the compressed integer within the overflow area and update the counter of overflowed numbers
                for bitIndex, bitElem in enumerate(correctedBitVal):
                    overflowArr[overflowStartPos+1+bitIndex] = True if bitElem == "1" else False
                overflowCount += 1
                continue
            
            # If the number is in normal area, indicate it
            compressedArr[startPos] = False
                
            # Put the sign
            if bitVal.startswith("-"):
                compressedArr[startPos+1] = True
            else:
                compressedArr[startPos+1] = False
            
            # Correct the length of bits to maxBitLength
            correctedBitVal = bitVal[-maxBitLength:].strip("-")
            correctedBitVal = ("0"*(maxBitLength-len(correctedBitVal))+correctedBitVal)[:maxBitLength+1]
            
            # Put the compressed integer in the correct place
            for bitIndex, bitElem in enumerate(correctedBitVal):
                compressedArr[startPos+2+bitIndex] = True if bitElem == "1" else False
        
        return compressedArr, maxBitLength, overflowArr, maxOverflowBitLength, len(arr)
        
    def decompress(self, *args:tuple[Any]) -> np.ndarray[int]:
        
        # Retrive and initialise necessary information
        compressedArr, maxBitLength, overflowArr, maxOverflowBitLength, initialLength, *_ = args
        decompressedArr = []
        overflowCount = 0
        
        # Loop through the compressed array
        for arrIndex in range(initialLength):
            
            # Compute the position to look at
            startPos = arrIndex*(maxBitLength+2) - overflowCount*(maxBitLength+1)
            
            # If value in overflow area, look in overflow area
            if compressedArr[startPos] == True:
                # Compute corresponding position within overflow area
                overflowStartPos = overflowCount * (maxOverflowBitLength+1)
                
                # Check if the value is negative and get the compressed integer
                neg = overflowArr[overflowStartPos]
                val = overflowArr[overflowStartPos+1:overflowStartPos+maxOverflowBitLength+1]
                
                # Transform the compressed integer and decode it
                decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
                decompressedArr.append(int(("-" if neg else "") + "".join(decompressedVal), base=2))
                
                # Update overflow count
                overflowCount += 1
                continue
            
            # If the value is not in overflow area, then get directly from the compressed array
            neg = compressedArr[startPos+1]
            val = compressedArr[startPos+2:startPos+2+maxBitLength]
            
            # and decode it before adding it to the decompressed array
            decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
            decompressedArr.append(int(("-" if neg else "") + "".join(decompressedVal), base=2) if decompressedVal != [] else 0)
        
        return np.array(decompressedArr)    

    def get(self, i:int, *args:tuple[Any]) -> int:
        
        # Retrieve necessary informations
        compressedArr, maxBitLength, overflowArr, maxOverflowBitLength, initialLength, *_ = args
        
        # Loop until index equal the one we want
        overflowCount = 0
        for arrIndex in range(initialLength):
            
            # Compute the index we want to look at in the compressed array
            lookAt = arrIndex*(maxBitLength+2) - overflowCount*(maxBitLength+1)
            
            # If the index is the one we want
            if arrIndex == i:
                # Check if it is within the overflow area
                if compressedArr[lookAt] == True:
                    
                    # Compute corresponding position within overflow area
                    overflowStartPos = overflowCount * (maxOverflowBitLength+1)
                
                    # Check if the value is negative and get the compressed integer
                    neg = overflowArr[overflowStartPos]
                    val = overflowArr[overflowStartPos+1:overflowStartPos+maxOverflowBitLength+1]
                    
                    # Transform the compressed integer and decode it
                    decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
                    return int(("-" if neg else "") + "".join(decompressedVal), base=2)
                
                # If the value is not in overflow area, then get directly from the compressed array
                neg = compressedArr[lookAt+1]
                val = compressedArr[lookAt+2:lookAt+2+maxBitLength]
                
                # and decode it before adding it to the decompressed array
                decompressedVal = ["0" if i == False else "1" for i in val.tolist()]
                if decompressedVal == []:
                    return 0
                return int(("-" if neg else "") + "".join(decompressedVal), base=2)
            
            # If it is not the one we want and it is in the overflow area, update the shift
            if compressedArr[lookAt] == True:
                overflowCount += 1


if __name__ == "__main__":
    arr = np.array([0])
    oC = OverflowCompressor(12)
    
    val = oC.compress(arr)
    
    print(arr[0] == oC.get(0, *val)) 
    
    print(sum(arr != oC.decompress(*val)))