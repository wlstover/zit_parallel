# rng.pxd
cdef class RandomNumberGenerator:
    cdef long last
    def __init__(self, long seed): ...