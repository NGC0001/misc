import numpy as np
import time
import sys
import matplotlib.pyplot as plt

K = 1024
M = 1024 * K
G = 1024 * M


class PrimeHolder():
    def __init__(self):
        self.ArrayLength = 1 * M
        self.MaxArrayNum = 1 * M
        self.MAX_NUMBER_OF_PRIMES = self.ArrayLength * self.MaxArrayNum
        self.MAX_PRIME_LIMIT = sys.maxsize
        self.HARDWARE_MAX_ARRAY_LENGTH = 1 * G
        self.arrayList = []
        array = np.zeros(self.ArrayLength, dtype=np.uint64)
        array[0] = 2
        self.arrayList.append(array)
        self.arrayMaxPrime = np.zeros(self.MaxArrayNum, dtype=np.uint64)
        self.arrayMaxPrime[0] = 2
        self.numLastArray = 1
        self.minNotJudged = 3

    def iter_current_list(self):
        for i in range(len(self.arrayList)-1):
            array = self.arrayList[i]
            for p in array:
                yield p
        array = self.arrayList[-1]
        for i in range(self.numLastArray):
            yield array[i]

    def iter_current_list_skip(self, n):
        g = self.iter_current_list()
        for i in range(n):
            next(g)
        for p in g:
            yield p

    def current_number_of_primes(self):
        return self.ArrayLength * (len(self.arrayList) - 1) + self.numLastArray

    def push_back(self, array, end):
        reslen = self.ArrayLength - self.numLastArray
        if len(array) == 0:
            pass
        elif len(array) <= reslen:
            self.arrayList[-1][self.numLastArray:self.numLastArray+len(array)] = array
            self.numLastArray += len(array)
            self.arrayMaxPrime[len(self.arrayList)-1] = array[-1]
        else:
            numOldList = len(self.arrayList)
            self.arrayList[-1][self.numLastArray:] = array[:reslen]
            self.arrayMaxPrime[numOldList-1] = self.arrayList[-1][-1]
            array = array[reslen:]
            remainlen = len(array) % self.ArrayLength
            numNew = len(array) // self.ArrayLength
            if remainlen == 0:
                numNew -= 1
                remainlen = self.ArrayLength
            if numNew > 0:
                self.arrayList.extend(np.split(array[:-remainlen], numNew))
                for i in range(numNew):
                    self.arrayMaxPrime[numOldList+i] = self.arrayList[numOldList+i][-1]
                array = array[-remainlen:]
            self.arrayList.append(np.zeros(self.MaxArrayNum, dtype=np.uint64))
            self.arrayList[-1][:remainlen] = array
            self.numLastArray = remainlen
            self.arrayMaxPrime[numOldList+numNew] = array[-1]
        self.minNotJudged = end

    def judge_till(self, judgeTill):
        start = self.minNotJudged
        if judgeTill <= start:
            return
        maxTill = start * start
        maxTillHardware = start + 2 * self.HARDWARE_MAX_ARRAY_LENGTH 
        end = judgeTill
        end = end if end <= maxTill else maxTill
        end = end if end <= maxTillHardware else maxTillHardware
        if start % 2 == 0:
            start += 1
        if end % 2 == 0:
            end += 1
        numJudge = (end - start) // 2
        array = np.arange(start, end, 2, dtype=np.uint64)
        maskArray = np.ones(numJudge, dtype=np.bool)
        for p in self.iter_current_list_skip(1):
            # firstPos = (p - start % p) % p
            first2PDiff = (2*p) - start % (2*p)
            firstPDiff = (first2PDiff + p) % (2*p)
            firstPos = firstPDiff // 2
            posArray = np.arange(firstPos, numJudge, p, dtype=np.uint64)
            maskArray[posArray] = False
            if p * p >= end:
                break
        array = array[maskArray]
        self.push_back(array, end)
        if end < judgeTill:
            self.judge_till(judgeTill)

    def judge_next_chunck(self, num_to_judge):
        start = self.minNotJudged
        judgeTill = start + num_to_judge
        self.judge_till(judgeTill)

    def try_to_judge_next_k_primes(self, k):
        num = int(k * np.log(self.minNotJudged))
        minnum = 20 * self.ArrayLength
        num = num if num > minnum else minnum
        # maxnum = self.HARDWARE_MAX_ARRAY_LENGTH
        # num = num if num < maxnum else maxnum
        self.judge_next_chunck(num)

    def judge_at_least_n_primes(self, n):
        while self.current_number_of_primes() < n:
            self.try_to_judge_next_k_primes(k=n-self.current_number_of_primes())

    def try_to_fill_next_k_arrays(self, k=1):
        multiple = int(k * np.log(self.minNotJudged))
        minmultiple = 20
        multiple = multiple if multiple > minmultiple else minmultiple
        # maxmultiple = self.HARDWARE_MAX_ARRAY_LENGTH // self.ArrayLength
        # multiple = multiple if multiple < maxmultiple else maxmultiple
        num_to_judge = multiple * self.ArrayLength
        self.judge_next_chunck(num_to_judge)

    def fill_at_least_n_arrays(self, n):
        while n > len(self.arrayList) - 1:
            self.try_to_fill_next_k_arrays(k=n+1-len(self.arrayList))

    def isprime(self, n):
        need = int(np.sqrt(n)) + 1
        if self.minNotJudged <= need:
            self.judge_till(need + 1)
        whichList = np.searchsorted(self.arrayMaxPrime[:len(self.arrayList)], n)
        if whichList < len(self.arrayList):
            if n in self.arrayList[whichList]:
                return True
            else:
                return False
        else:
            for p in self.iter_current_list():
                if n % p == 0:
                    return False
            return True

    def get_nth_prime(self, n):
        self.judge_at_least_n_primes(n)
        s = n // self.ArrayLength
        r = n % self.ArrayLength
        if r == 0:
            r = self.ArrayLength
            s -= 1
        r -= 1
        return self.arrayList[s][r]

    def get_first_n_primes(self, n):
        self.judge_at_least_n_primes(n)
        res = np.zeros(n, dtype=np.uint64)
        s = n // self.ArrayLength
        r = n % self.ArrayLength
        for i in range(s):
            res[i*self.ArrayLength:(i+1)*self.ArrayLength] = self.arrayList[i]
        if r != 0:
            res[s*self.ArrayLength:] = self.arrayList[s][:r]
        return res

    def get_primes_le(self, n):
        self.judge_till(n + 1)
        whichList = np.searchsorted(self.arrayMaxPrime[:len(self.arrayList)], n)
        if whichList < len(self.arrayList) - 1:
            pos = np.searchsorted(self.arrayList[whichList], n, side='right')
            return self.get_first_n_primes(whichList * self.ArrayLength + pos)
        elif whichList == len(self.arrayList) - 1:
            pos = np.searchsorted(self.arrayList[whichList][:self.numLastArray], n, side='right')
            return self.get_first_n_primes(whichList * self.ArrayLength + pos)
        else:
            return self.get_first_n_primes(self.current_number_of_primes())

    def __iter__(self):
        ilist = 0
        while True:
            while ilist + 1 == len(self.arrayList):
                self.try_to_fill_next_k_arrays(k=1)
            for i in range(self.ArrayLength):
                yield self.arrayList[ilist][i]
            ilist += 1


if __name__ == '__main__':

    ph = PrimeHolder()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10), subplot_kw=dict(polar=True))
    num1 = 50000
    primes1 = ph.get_primes_le(num1)
    theta1 = primes1
    r1 = primes1
    ax1.scatter(theta1, r1, c='b', s=0.1)
    ax1.grid(False)
    ax1.set_title('{} primes'.format(num1))
    ax1.set_xticks([])
    ax1.set_yticks([])
    num2 = 15000000
    primes2 = ph.get_primes_le(num2)
    theta2 = primes2
    r2 = primes2
    ax2.scatter(theta2, r2, c='b', s=0.01)
    ax2.grid(False)
    ax2.set_title('{} primes'.format(num2))
    ax2.set_xticks([])
    ax2.set_yticks([])
    plt.show()
    raise SystemExit

    ph = PrimeHolder()
    a = ph.get_primes_le(16290047)
    b = ph.get_first_n_primes(1048576)
    print(a.shape, a)
    print(b.shape, b[-1])
    raise SystemExit

    ph = PrimeHolder()
    select = {1, 10, 100, 300, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000}
    st = time.time()
    for i, p in enumerate(ph):
        n = i+1
        if n in select:
            et = time.time()
            print('the {}th prime is {}, time consumed: {}s'.format(n, p, et-st))
        if n >= 100000000:
            et = time.time()
            print('{} primes, total time consumed: {}s'.format(n, et-st))
            break
    raise SystemExit

    ph = PrimeHolder()
    select = [1, 100, 1000, 10000, 100000, 1000000, M, 10000000, 100000000, 1000000000]
    st = time.time()
    for n in select:
        p = ph.get_nth_prime(n)
        et = time.time()
        print('the {}th prime is {}, time consumed: {}s'.format(n, p, et-st))
    raise SystemExit

