import numpy as np
from scipy.stats import boltzmann

# Random Number Generator
rng = np.random.RandomState(0)

# Boltzmann Number Generator
# Boltzmann distribution is a distribution used in many fields, especially in physics and statistical mechanics. It is also known as
# truncated planck distribution or truncated discrete exponential distribution. In this distribution, "small" number are more likely to appears.
# https://en.wikipedia.org/wiki/Boltzmann_distribution
# https://docs.scipy.org/doc/scipy/tutorial/stats/discrete_boltzmann.html
lam = 10**-4
smallBoltzmann = boltzmann(lam, 2**16-1)

# Tests sets
testSets = {
    "smallInt_small": rng.randint(-2**8+1, 2**8, 1_000),
    "smallInt_medium": rng.randint(-2**8+1, 2**8, 100_000),
    "smallInt_large": rng.randint(-2**8+1, 2**8, 1_000_000),
    "smallInt_superLarge": rng.randint(-2**8+1, 2**8, 4_000_000),
    
    "largeInt_small": rng.randint(-2**16+1, 2**16, 1_000),
    "largeInt_medium": rng.randint(-2**16+1, 2**16, 100_000),
    "largeInt_large": rng.randint(-2**16+1, 2**16, 1_000_000),
    "largeInt_superLarge": rng.randint(-2**16+1, 2**16, 4_000_000),
    
    "boltzmann_small": smallBoltzmann.rvs(1_000, random_state=0),
    "boltzmann_medium": smallBoltzmann.rvs(100_000, random_state=1),
    "boltzmann_large": smallBoltzmann.rvs(1_000_000, random_state=2),
    "boltzmann_superLarge": smallBoltzmann.rvs(4_000_000, random_state=2),
    
    "superLargeInt_small": rng.randint(-2**31, 2**31-1, 1_000),
    "superLargeInt_medium": rng.randint(-2**31, 2**31-1, 100_000),
    "superLargeInt_large": rng.randint(-2**31, 2**31-1, 1_000_000)
}

# Save the datas
for key, value in testSets.items():
    with open(f"IN\\{key}.in", "w") as file:
        value.tofile(file, sep=" ")

