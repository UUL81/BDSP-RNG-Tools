from xorshift import Xorshift
from random import randint

# randomly generate a state to use
seed = [randint(0,0xFFFFFFFF),randint(0,0xFFFFFFFF),randint(0,0xFFFFFFFF),randint(0,0xFFFFFFFF)]
# amount of blinks used to reidentify
blink_len = 20
# max advances to search
max_advance = 10000
# advance when starting reidentify
reident_advance = 1001

# init rng
rng = Xorshift(*seed)
# advance pre-reident
rng.advance(reident_advance)

# simulate observing player blinks
counter = 0
observed_blinks = []
wait = rng.rangefloat(3,12)
while observed_blinks.count(True) < blink_len:
    if counter % 1 <= 0.1:
        observed_blinks.append(rng.next() & 0b1110 == 0)
    if wait <= 0:
        wait = rng.rangefloat(3,12)
    wait -= 0.1
    counter += 0.1

# time elapsed during reidentification
reident_time = len(observed_blinks)
# account for the maximum amount of extra advances caused by pokemon blinks
possible_length = int(reident_time*4//3)

# begin to calc current advance
possible = []
rng = Xorshift(*seed)
rng.next()
blink_rands = [int((r&0b1110)==0) for r in rng.get_next_rand_sequence(max_advance)]
# loop through all possible advances
for adv in range(max_advance-possible_length):
    # slice blink_rands to only give only the random values that could happen since this advance during reidentification 
    blinks = blink_rands[adv:adv+possible_length]
    # init index variables
    i = 0
    j = 0
    # difference = the amount of pokemon blinks that must have happened for this to be possible
    differences = []
    try:
        while i < reident_time:
            diff = 0
            # if observed_blinks[i] != blinks[j], assuming this is the correct advance, a pokemon blink must have happened inbetween
            while observed_blinks[i] != blinks[j]:
                diff += 1
                j += 1
            if diff != 0:
                differences.append(diff)
            j += 1
            i += 1
    # if pattern does not line up, check next advance
    except IndexError:
        continue
    # at this point, only a handful of potential advances have made it through
    # calculate the total amount of pokemon blinks that have happened during reident
    cress_pred_blinks = sum(differences)
    # add a tuple to possible that can be sorted by the amount of pokemon blinks
    possible.append((cress_pred_blinks,adv))
# get the tuple with the lowest amount of pokemon blinks 
cresselia_blinks, advance = min(possible)
# display our prediction
print(f"{advance=} {cresselia_blinks=}")