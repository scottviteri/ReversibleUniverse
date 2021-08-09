import numpy as np

def identity_vertex_map(b1,b2):
    if   b1 and      b2: return (True, True)
    elif b1 and not(b2): return (True, False)
    elif not(b1) and b1: return (False, True)
    else :              return (False, False)

def num_to_vertex(n):
    if   n==0: return (False, False)
    elif n==1: return (True, False)
    elif n==2: return (True, True)
    else:      return (False, True)

def nums_to_vertex_map(l): # eg l = [1,2,3,0]
    def vmap(b1,b2):
     if   not(b1) and not(b2): return num_to_vertex(l[0])
     elif     b1  and not(b2): return num_to_vertex(l[1])
     elif     b1  and     b2 : return num_to_vertex(l[2])
     else                   : return num_to_vertex(l[3])
    return vmap

def transition_even(S,vertex_map):
    l = S.shape[0]
    out = np.zeros(l)
    for i in range(0,l,2):
        out[i],out[i+1] = vertex_map(S[i],S[i+1])
    return out

def transition_odd(S,vertex_map):
    l = S.shape[0]
    out = np.zeros(l)
    for i in range(1,l-1,2):
        out[i],out[i+1] = vertex_map(S[i],S[i+1])
    out[l-1], out[0] = vertex_map(S[l-1],S[0])
    return out

def transitions_even(S,vertex_map,count):
    out = S
    for i in range(count):
        if i!=0 and all(out == S): return i
        out = transition_even(out,vertex_map)

def transitions_odd(S,vertex_map,count):
    out = S
    for i in range(count):
        if i!=0 and all(out == S): return i
        out = transition_odd(out,vertex_map)

def simulate(S,vmap_list,count):
    run_even = True
    vertex_map = nums_to_vertex_map(vmap_list)
    out = S
    for i in range(count):
        if i!=0 and all(out == S): return i
        if run_even: out = transition_even(out, vertex_map)
        else: out = transition_odd(out, vertex_map)
        run_even = not(run_even)

def get_periodicity(S,vmap_list,count):
    run_even = True
    vertex_map = nums_to_vertex_map(vmap_list)
    out = S
    for i in range(count):
        if i!=0 and all(out == S): return i
        if run_even: out = transition_even(out, vertex_map)
        else: out = transition_odd(out, vertex_map)
        run_even = not(run_even)

def rand_bitstring(n): return np.random.randint(0,2,n).astype('float')

def rand_vmap_list(n):
    l = np.array(range(n))
    np.random.shuffle(l)
    return l

# size two reversible functions lead to too many cycles!
#  the universe doesn't have a cycle problem either due to infinite or very large bitstring
#  in practice finding that periodicity is around size of bitstring, or a few times larger
# get_periodicity(rand_bitstring(32),rand_vmap_list(4),100) <- commonly 32
# but this is no good <- want to increase entropy
#  aka info should get spread out

def num_to_binary(n, bitlength=None):
    def num_to_binary_aux(n,l):
        if n==0:
            return l
        if n&1:
            l.append(True)
        else:
            l.append(False)
        n = n>>1
        return num_to_binary_aux(n, l)
    out = num_to_binary_aux(n,[])[::-1]
    if bitlength:
        out = [False]*(bitlength - len(out)) + out
    return out

def num_to_3vertex(n):
    return num_to_binary(n,bitlength=3)

def binary_to_num(bs):
    if bs.shape[0]==0: return 0
    return int(bs[-1]) + 2*binary_to_num(bs[:-1])

def nums_to_3vertex_map(l): # eg l = [5,7,3,4,1,2,0,6]
    return (lambda bs: num_to_3vertex(l[binary_to_num(bs)])) #bs is a numpy array

identity_3map = nums_to_3vertex_map(list(range(8)))
def transition_mod3_rem(S,vertex_map,rem):
    l = S.shape[0]
    out = np.zeros(l)
    for i in range(rem,l,3):
        local_outs = vertex_map(S.take(np.arange(i,i+3),mode='wrap'))
        for k in range(len(local_outs)):
            out[(i+k)%l] = local_outs[k]
    return out


def simulate3(S,vmap_list,max_count=10000):
    assert(S.shape[0]%3==0)
    vertex_map = nums_to_3vertex_map(vmap_list)
    print(S)
    out, rem = S, 0
    for count in range(max_count):
        if count!=0 and all(out == S): return count
        out = transition_mod3_rem(out,vertex_map,rem)
        rem = (rem+1)%3
    return count

def cycle(n):
    return list(range(1,n)) + [0]

# should macrostates be in time or space or both
#  probably space
#  could have macro state of parity, or majority, or nth
#   could just use any boolean function really <- boolean polynomial?

# could then learn dynamics on macro state
#  but dynamics can be irreversible

# good macrostate is one that the dynamics act like a function
#  aka a given input yields a given output
#  so goodness of macrostates/abstractions depend on dynamics

# Can search for a good abstraction
#  aka a function from A: B^n -> B^m
#  st there exists a transition T':B^m->B^m where A(T(S)) = T'(A(S))

# can measure how much of a function T' is
#  could count the number of inputs with multiple outputs

# in_dim must divide bitstring length
def abstract(in_dim, A, bitstring):
    out_dim = A(bitstring[:in_dim]).shape[0]
    return np.concatenate(list(map(A,np.split(bitstring, bitstring.shape[0]//out_dim))))

def xor(l): return np.array([l[0] == l[1]])
