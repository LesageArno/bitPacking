from Compressor.AbstractCompressor import Compressor
from typing import Any
import numpy as np

INT_ENCODING_SIZE = 32 #32 bits per integer

class OverflowCompressor(Compressor):
    def __init__(self):
        super().__init__()
        
    def compress(self, arr:np.ndarray[int], threshold:int|float = 0.7) -> tuple[np.ndarray[bool],int,np.ndarray[bool],int,int]:
        
        # If the threshold is a float, take the corresponding quantile bit_length as threshold for overflow. Otherwise, use the give bit threshold
        overflowThresholdBitLength = np.quantile(arr, threshold).__abs__().__floor__().bit_length() if isinstance(threshold, float) else threshold
        
        # Compute the max bit length of the supremum element in the overflow area and outside
        maxOverflowBitLength = int(arr[arr.__abs__() >= 2**overflowThresholdBitLength].__abs__().max()).bit_length()
        maxBitLength = int(arr[arr.__abs__() < 2**overflowThresholdBitLength].__abs__().max()).bit_length()
        
        # Compute the length of the areas and create the compressed and overflow array
        compressedArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxBitLength+1) / INT_ENCODING_SIZE)
        overflowArrayLength = INT_ENCODING_SIZE * float.__ceil__(len(arr) * (maxOverflowBitLength+1) / INT_ENCODING_SIZE)
        compressedArr = np.zeros(compressedArrayLength, dtype=bool)
        overflowArr = np.zeros(overflowArrayLength, dtype=bool)

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
                overflowArr[overflowStartPos+1:overflowStartPos+maxOverflowBitLength+1] = [True if bitElem == "1" else False for bitElem in correctedBitVal]
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
            correctedBitVal = "0"*(maxBitLength-len(correctedBitVal))+correctedBitVal
            
            # Put the compressed integer in the correct place
            compressedArr[startPos+2:startPos+2+maxBitLength] = [True if bitElem == "1" else False for bitElem in correctedBitVal]
        
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
            decompressedArr.append(int(("-" if neg else "") + "".join(decompressedVal), base=2))
        
        return np.array(decompressedArr, dtype=np.int32)    

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
                return int(("-" if neg else "") + "".join(decompressedVal), base=2)
            
            # If it is not the one we want and it is in the overflow area, update the shift
            if compressedArr[lookAt]:
                overflowCount += 1


if __name__ == "__main__":
    arr_SmallInt = np.random.randint(-2**8+1, 2**8, 100_000)
    oC = OverflowCompressor()
    
    val = oC.compress(arr_SmallInt)
    
    print(arr_SmallInt[18967] == oC.get(18967, *val)) 
    
    print(sum(arr_SmallInt != oC.decompress(*val)))