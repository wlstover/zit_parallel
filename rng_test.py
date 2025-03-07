import sys

class RandomNumberGenerator:
    def __init__(self, seed=1):
        self.last = seed  # Initialize with a seed

    def long_integer(self):
        """
        Generates an integer-valued random number in the interval [1, INT_MAX - 1].
        Implements the minimal standard LCG from Bratley, Fox, and Schrage (1987).
        """
        INT_MAX = sys.maxsize  # Typically 2^31 - 1 on 32-bit, 2^63 - 1 on 64-bit systems
        k = self.last // 127773
        self.last = 16807 * (self.last - k * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX  # Ensure non-negative value
        return self.last

    def integer_in_range(self, min_val, max_val):
        """
        Generates an integer-valued random number in the range [min_val, max_val].
        """
        return min_val + self.long_integer() % (max_val - min_val + 1)

# Example usage:
rng = RandomNumberGenerator(seed=42)
print(rng.integer_in_range(1, 100))  # Example: Generates a number between 1 and 100
