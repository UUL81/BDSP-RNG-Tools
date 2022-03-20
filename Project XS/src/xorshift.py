"""Xorshift Random Number Generator"""
class Xorshift:
    """Xorshift Random Number Generator"""
    def __init__(self,seed_0,seed_1,seed_2,seed_3):
        self.seed_0 = seed_0
        self.seed_1 = seed_1
        self.seed_2 = seed_2
        self.seed_3 = seed_3

    def next(self):
        """Generate the next random number"""
        temp = self.seed_0 ^ self.seed_0 << 11 & 0xFFFFFFFF
        self.seed_0 = self.seed_1
        self.seed_1 = self.seed_2
        self.seed_2 = self.seed_3
        self.seed_3 = temp ^ temp >> 8 ^ self.seed_3 ^ self.seed_3 >> 19

        return self.seed_3

    def prev(self):
        """Generate the previous random number"""
        temp = self.seed_2 >> 19 ^ self.seed_2 ^ self.seed_3
        temp ^= temp >> 8
        temp ^= temp >> 16

        temp ^= temp << 11 & 0xFFFFFFFF
        temp ^= temp << 22 & 0xFFFFFFFF

        self.seed_0 = temp
        self.seed_1 = self.seed_0
        self.seed_2 = self.seed_1
        self.seed_3 = self.seed_2

        return self.seed_3

    def advance(self,length:int):
        """Skip advances of length"""
        self.get_next_rand_sequence(length)

    def range(self,minimum:int,maximum:int)->int:
        """Generate random integer in range [minimum,maximum)

        Args:
            minimum ([int]): minimum
            maximum ([int]): maximam

        Returns:
            int: random integer
        """
        return self.next() % (maximum-minimum) + minimum

    def randfloat(self)->float:
        """Generate random float in range [0,1]

        Returns:
            float: random float
        """
        return (self.next() & 0x7fffff) / 8388607.0

    def rangefloat(self,minimum:float,maximum:float)->float:
        """Generate random float in range [minimum,maximum]

        Args:
            minimum (float): minimum
            maximum (float): maximam

        Returns:
            float: random float
        """
        temp = self.randfloat()
        return temp * minimum + (1-temp) * maximum

    def get_next_rand_sequence(self,length):
        """Generate a the next random sequence of length"""
        return [self.next() for _ in range(length)]

    def get_prev_rand_sequence(self,length):
        """Generate the previous random sequence of length"""
        return [self.prev() for _ in range(length)]

    def get_state(self):
        """Get the state of the RNG"""
        return [self.seed_0, self.seed_1, self.seed_2, self.seed_3]

    def set_state(self, seed_0, seed_1, seed_2, seed_3):
        """Set state of the RNG"""
        self.seed_0 = seed_0
        self.seed_1 = seed_1
        self.seed_2 = seed_2
        self.seed_3 = seed_3
