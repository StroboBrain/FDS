# Lecuture: Foundations of Distributed Systems
# Exercise 8
# Task 4: Fully homomorphic encryption

import concrete.numpy as cnp
import numpy as np

# Calculates the integer mean of an array of length 6.
@cnp.compiler({"x": "encrypted"})
def meanOf6(x):
	return np.sum(x).astype(np.int64) // 6

# To return the mean with two decimal places, the input-array is first scaled by a factor of 100
# before encryptinm, calculating the mean, and decrypting, then the result is scaled by a factor of 1/100
# back to the original scale.
def meanOf6with2DPs(input, circuit):
	input *= 100
	return circuit.encrypt_run_decrypt(input) / 100

# Calculates the integer mean of an array of length 7.
@cnp.compiler({"x": "encrypted"})
def meanOf7(x):
	return np.sum(x).astype(np.int64) // 7


# Testing for meanOf6 and meanOf6with2DPs

# Apparently, concrete-numpy requires a sample of possible inputs.
# The range specified influences what can actually be calculated.
# For example, using np.random.randint(-2**12, 2**12, size=6) instead would limit the calculation to positive values.
inputset = [np.random.randint(-2**12, 2**12, size=6) for _ in range(10)]
circuit6 = meanOf6.compile(inputset)

# Test 1: Example with positive mean with one non-zero decimal place.
print("--- Test 1 ---")
input = np.array([1,2,3,4,5,6])
output = circuit6.encrypt_run_decrypt(input)
assert output == 3
print("output [0 dp]:", output)

output = meanOf6with2DPs(input, circuit6)
assert output == 3.5
print("output [2 dp]:", output)

# Test 2: Example with positive mean with two non-zero decimal place.
print("--- Test 2 ---")
input = np.array([2,2,2,2,4,4])
output = circuit6.encrypt_run_decrypt(input)
assert output == 2
print("output [0 dp]:", output)

output = meanOf6with2DPs(input, circuit6)
assert output == 2.66
print("output [2 dp]:", output)

# Test 3: Example with negative mean with one non-zero decimal place
print("--- Test 3 ---")
input = np.array([-1,-2,-3,-4,-5,-6])
output = circuit6.encrypt_run_decrypt(input)
assert output == -4
print("output [0 dp]:", output)

output = meanOf6with2DPs(input, circuit6)
assert output == -3.5
print("output [2 dp]:", output)

# Test 4: Example with negative mean with two non-zero decimal place.
print("--- Test 4 ---")
input = np.array([-2,-2,-2,-2,-4,-4])
output = circuit6.encrypt_run_decrypt(input)
assert output == -3
print("output [0 dp]:", output)

output = meanOf6with2DPs(input, circuit6)
assert output == -2.67
print("output [2 dp]:", output)


# Testing for meanOf7

# Apparently, concrete-numpy requires a sample of possible inputs.
inputset = [np.random.randint(-2**12, 2**12, size=7) for _ in range(10)]
circuit7 = meanOf7.compile(inputset)

# Test 5: Example with positive mean.
print("--- Test 5 ---")
input = np.array([1,2,3,4,5,6,7])
output = circuit7.encrypt_run_decrypt(input)
assert output == 4
print("output [0 dp]:", output)

# Test 6: Example with negative mean.
print("--- Test 6 ---")
input = np.array([-1,-2,-3,-4,-5,-6,-7])
output = circuit7.encrypt_run_decrypt(input)
assert output == -4
print("output [0 dp]:", output)
