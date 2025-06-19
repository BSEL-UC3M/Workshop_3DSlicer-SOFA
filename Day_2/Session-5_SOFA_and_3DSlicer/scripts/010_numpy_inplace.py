import numpy as np

a = np.array([1, 2, 3, 4, 5])

# Assigning a new array to 'a' creates a new object
a = np.array([10, 20, 30, 40, 50])
print("After assignment, 'a' is:", a)

# Using a slice to modify 'a' in-place
a[:] = [100, 200, 300, 400, 500]
print("After in-place modification, 'a' is:", a)

# Verifying that the array object is the same
b = a
a[:] = [1, 2, 3, 4, 5]
print("After modifying 'a', 'b' is also changed:", b)
