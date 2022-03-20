"""Module for calculating Xorshift state based on observed information"""
from bisect import bisect
from functools import reduce
import numpy as np

def get_zero(size=32):
    """Get a matrix of the size provided filled with zeros"""
    return np.zeros((size,size),dtype="uint8")

def get_identity(size=32):
    """Get an identity matrix of the size provided"""
    return np.identity(size,dtype="uint8")

def get_shift(shift,size=32):
    """Get an identity matrix of the size provided shifted accordingly"""
    return np.eye(size,k=shift,dtype="uint8")

def get_trans():
    """Create the transformation matrix used for Xorshift state calculation"""
    trans = np.block([
        [get_zero(),get_identity(),get_zero(),get_zero()],
        [get_zero(),get_zero(),get_identity(),get_zero()],
        [get_zero(),get_zero(),get_zero(),get_identity()],
        [(get_identity()^get_shift(-8))@(get_identity()^get_shift(11))%2,
         get_zero(),get_zero(),get_identity()^get_shift(-19)],
        ])
    return trans

def get_ref_matrix(intervals,rows = 39):
    """Create the matrix to be referenced for Xorshift state calculation based
       on player blink intervals"""
    intervals = intervals[:rows]
    base_mat = get_trans()
    advance_mat = get_trans()

    ref_mat = np.zeros((4*rows,128),"uint8")
    for i in range(rows):
        ref_mat[4*i:4*(i+1)] = base_mat[-4:]
        for _ in range(intervals[i]):
            base_mat = base_mat@advance_mat%2
    return ref_mat

def get_ref_matrix_munchlax(intervals):
    """Create the matrix to be referenced for Xorshift state calculation based
       on munchlax intervals"""
    intervals = intervals[::-1]
    section = [0, 3.4333333333333336, 3.795832327504833, 3.995832327504833, 4.358332394560066,
               4.558332394560066, 4.9208324616153, 5.120832461615299, 5.483332528670533,
               5.683332528670532, 6.045832595725767, 6.2458325957257665, 6.608332662781,
               6.808332662780999, 7.170832729836233, 7.370832729836232, 7.733332796891467,
               7.933332796891467, 8.2958328639467, 8.4958328639467, 8.858332931001934,
               9.058332931001933, 9.420832998057167, 9.620832998057166, 9.9833330651124,
               10.1833330651124, 10.545833132167635, 10.745833132167634, 11.108333199222866,
               11.308333199222865, 11.6708332662781, 11.8708332662781, 12.233333333333334
               ]
    base_mat = get_trans()
    advance_mat = get_trans()

    ref_mat = np.zeros((144,128),"uint8")
    safe_intervals = []
    for i in range(36):
        #intervals[-1]を挿入した際のインデックスが奇数だと危険な値の可能性がある
        is_carriable = bisect(section,intervals[-1])%2==1
        while is_carriable:
            #スキップする
            base_mat = base_mat@advance_mat%2
            #危険な値を除外
            intervals.pop()
            is_carriable = bisect(section,intervals[-1])%2==1
        ref_mat[4*i:4*(i+1)] = base_mat[105:109]
        base_mat = base_mat@advance_mat%2
        safe_intervals.append(intervals.pop())
    return ref_mat, safe_intervals

def gauss_jordan(mat,observed:list):
    """Convert observered information and reference matrix to 128 bit Xorshift state
       via gauss jordan elimination"""
    height,width = mat.shape

    bitmat = [list2bitvec(mat[i]) for i in range(height)]

    res = observed.copy()
    #forward elimination
    pivot = 0
    for i in range(width):
        isfound = False
        for j in range(i,height):
            if isfound:
                check = 1<<(width-i-1)
                if bitmat[j]&check==check:
                    bitmat[j] ^= bitmat[pivot]
                    res[j] ^= res[pivot]
            else:
                check = 1<<(width-i-1)
                if bitmat[j]&check==check:
                    isfound = True
                    bitmat[j],bitmat[pivot] = bitmat[pivot],bitmat[j]
                    res[j],res[pivot] = res[pivot],res[j]
        if isfound:
            pivot += 1

    for i in range(width):
        check = 1<<(width-i-1)
        assert bitmat[i]&check>0

    #backward assignment
    for i in range(1,width)[::-1]:
        check = 1<<(width-i-1)
        for j in range(i)[::-1]:
            if bitmat[j]&check==check:
                bitmat[j] ^= bitmat[i]
                res[j] ^= res[i]
    return res[:width]

def bitvec2list(bitvec,size=128):
    """Convert bitvec of size to list of bits"""
    lst = [(bitvec>>i)&1 for i in range(size)]
    return np.array(lst[::-1])

def list2bitvec(lst):
    """Convert list of bits to bitvec"""
    bitvec = reduce(lambda p,q: (int(p)<<1)|int(q),lst)
    return bitvec

def reverse_states(rawblinks:list, intervals:list)->list:
    """Deduce state of Xorshift random number generator using player blinks and intervals"""
    blinks = []
    for blink in rawblinks:
        blinks.extend([0,0,0])
        blinks.append(blink)

    #print(blinks)
    ref_matrix = get_ref_matrix(intervals)
    lst_result = gauss_jordan(ref_matrix, blinks)
    bitvec_result = list2bitvec(lst_result)

    result = []
    for _ in range(4):
        result.append(bitvec_result&0xFFFFFFFF)
        bitvec_result>>=32

    result = result[::-1]#reverse order
    return result

def reverse_float_range(rand_float:float, minimum:float, maximum:float):
    """Convert random float back to original integer"""
    norm_f = (maximum-rand_float)/(maximum-minimum)
    return int(norm_f*8388607.0)&0x7fffff

def reverse_states_by_munchlax(intervals:list)->int:
    """Deduce state of Xorshift random number generator using munchlax blink intervals"""
    ref_matrix, safe_intervals = get_ref_matrix_munchlax(intervals)
    bitvectorized_intervals = [reverse_float_range(30.0*f,100,370)>>19 for f in safe_intervals]
    bitlst_intervals = []
    for bits in bitvectorized_intervals[::-1]:
        for _ in range(4):
            bitlst_intervals.append(bits&1)
            bits >>= 1
    bitlst_intervals = bitlst_intervals[::-1]

    bitvec_result = list2bitvec(gauss_jordan(ref_matrix, bitlst_intervals))
    result = []
    for _ in range(4):
        result.append(bitvec_result&0xFFFFFFFF)
        bitvec_result>>=32

    result = result[::-1]#reverse order
    return result
