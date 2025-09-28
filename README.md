# Software Engineering project: Data compressing for speed up transmission


### **Arno LESAGE** - *M1 Informatique (2025/2026), spé. IA, EUR DS4H, Université Côte d'Azur, France*


Transmission of integer arrays is part of one of the central problems of the internet. This project aims to implement three different method relying on *Bit Packing* for integer array compression in order to reduce the transmission delay $d_{\text{trans}}$.

More precisely, considering a finite length array of 32-bit encoded integer, we want to compress the contained information knowing that some integer might not require the full 32-bit space to fit in memory. This work is done via three different implementation of *Bit Packing*:

- **Split:** Letting the possibility for a 32-bit integer to be splitted between two 32-bit integer after compression,
- **No Split:** Prohibiting the split of an integer into two different integer after compression,
- **Overflow:** Same as split, but use a threshold to separate integers needing more bits and less bits in order to further optimise memory usage.

***Note:** One constraint apply to all of these methods. The order of the integer must be preserved and accessible even after compression and/or decompression.*

## Getting Started
This part contains instructions to properly set up the project and run it.

### Prerequisites
This project was developped using **Python 1.12.0** (install <a href="https://www.python.org/downloads/release/python-3120/">here</a>) and require the language to run properly.

Additionally, the project make usage of several external libraries (see <a href="OTHERS//requirements.txt">requirements.txt</a>) and therefore require the installation of <a href="https://pip.pypa.io/en/stable/installation/">pip</a> (the Python library manager).

To install the right version of each required library (NumPy, SciPy and PyTest), you may use the following command (Windows 10/11):

    pip install -r .\OTHERS\requirements.txt

### Installing

To install the project, download the zipped folder of this repository. Decompress it and open the folder as working directory using any IDE.

You can now use the integer array compression tools by creating a new Python script within the working directory and adding the following header:

```py
from main import BitPacking
mode = ... # between "split", "nosplit" or "overflow"
bP = BitPacking(mode)
```

A typical use example may be the following:
```py
from main import BitPacking
from typing import Any
import numpy as np

# Get Array and initialise bit packing
inArr:np.ndarray[int] = np.array([-892, 89, 760, 216, 14], dtype=np.int32)
bP = BitPacking("split")

# Feed with array 
bP.setArr(inArr)
bP.compress()

# Get compressed array
outArr:np.ndarray[bool], *_ = bP.getCompressedArr()
# [True True True False True True True True True False False False False False False True False True True False False True False True False True True True True True False False False False False False True True False True True False False False False False False False False False False True True True False False False False False False False False False False]

# Decompress array
bP.decompress()
decompressedArr = bP.getArr()
# [-892 89 760 216 14]
```

## Tests files

Explain how to run the automated tests for this system

### Sample Tests

Explain what these tests test and why

    Give an example

### Style test

Checks if the best practices and the right coding style has been used.

    Give an example

