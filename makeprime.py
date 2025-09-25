# Makeprime Python Version
import argparse
import random
import gmpy2
import signal
import psutil
import os
import sys
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
from multiprocessing.spawn import freeze_support

# Divisible by small primes
small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29,
                31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
                127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
                179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
                233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
                283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
                353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
                419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
                467, 479, 487, 491, 499, 503, 509, 521, 523, 541]

def divisible_by_small_primes(n: int) -> bool:
    for p in small_primes:
        if n % p == 0:
            return True
    return False

# Generate Candidate
def generate_candidate(digits: int, want_random: bool) -> int:
    candidate = (10**(digits-1))+1
    if want_random:
        candidate = random.randint(1, 10**digits) - 1
        if candidate % 2 == 0:
            candidate += 1
    while divisible_by_small_primes(candidate):
        candidate += 2
    return candidate

# Miller Rabin Implementation (default to 10 rounds)
def miller_rabin_prime_test(n, k = 10):
    if n < 2 or (n != 2 and not n & 1):
        return False
    if n < 6:
        return True

    s = 0
    d = n - 1
    while not d & 1:
        d >>= 1
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = gmpy2.powmod(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = gmpy2.powmod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# Find Prime
def find_prime(digits: int, want_twin: bool, want_random: bool) -> int:
    found = False
    candidate = generate_candidate(digits, want_random)
    while not found:
        if not want_twin and not divisible_by_small_primes(candidate) and miller_rabin_prime_test(candidate):
            found = True
        elif want_twin and not divisible_by_small_primes(candidate) and miller_rabin_prime_test(candidate) and miller_rabin_prime_test(candidate+2):
            found = True
        else:
            candidate += 2
    return candidate

# Find Prime Multicore
def find_prime_worker(c: int, twin: bool) -> int:
    found = False
    while not found:
        if not twin and not divisible_by_small_primes(c) and miller_rabin_prime_test(c):
            found = True
        elif twin and not divisible_by_small_primes(c) and miller_rabin_prime_test(c) and miller_rabin_prime_test(c+2):
            found = True
        else:
            c += 2
    return c

def find_prime_multi(digits: int, want_twin: bool, want_random: bool) -> int:
    candidate = generate_candidate(digits, want_random)
    num_procs = os.cpu_count()

    pool = ProcessPoolExecutor(max_workers=num_procs)
    futures = []
    for _ in range(num_procs):
        futures.append(pool.submit(find_prime_worker, candidate, want_twin))
        candidate += 1_000_000_000

    done, not_done = wait(futures, return_when=FIRST_COMPLETED)
    pool.shutdown(wait=False)

    return next(iter(done)).result()

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)

# Main program
if __name__ == '__main__':
    freeze_support()
    parser = argparse.ArgumentParser()
    parser.add_argument('digits', type=int, help='number of digits (must be 3 or more)')
    parser.add_argument('--twin', action="store_true", help='find consecutive primes')
    parser.add_argument('--random', action="store_true", help='use random starting point')
    parser.add_argument('--multi', action="store_true", help='use multiple cores')
    args = parser.parse_args()

    if args.digits < 3:
        print('must have at least 3 digits')
        exit(1)

    prime = find_prime_multi(args.digits, args.twin, args.random) if args.multi else find_prime(args.digits, args.twin, args.random)
    if args.digits > 4300:
        sys.set_int_max_str_digits(args.digits)
    print(prime)
    if args.twin:
        print(prime+2)

    if args.multi: kill_child_processes(os.getpid())