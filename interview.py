'''
Write the function uniqueDigits which takes in a (possibly negative) integer n  and returns True if each digit in n appears at 
most once. 
For instance, uniqueDigits(123) and uniqueDigits(-42) and uniqueDigits(816205) all return True because there are no duplicate digits. 
However, uniqueDigits(15112) returns False because it has three 1s and uniqueDigits(6106) returns False because it has two 6s.
This function should be recursive and should not use strings or loops. You should utilize wrapper functions. 
'''
def uniqueDigits(n):
    n = abs(n)
    rightDigits = set()
    return uniqueDigitsHelper(n, rightDigits)

def uniqueDigitsHelper(n, rightDigits):
    if n==0:
        return True
    else:
        digit = n%10
        if digit in rightDigits:
            return False
        else:
            rightDigits.add(digit)
        restOfNum = n//10
        return uniqueDigitsHelper(restOfNum, rightDigits)

def testUniqueDigits():
    print('Testing...', end='')
    assert(uniqueDigits(123)==True)
    assert(uniqueDigits(-42)==True)
    assert(uniqueDigits(92587)==True)
    assert(uniqueDigits(11)==False)
    assert(uniqueDigits(-4564)==False)
    print('Passed!')

testUniqueDigits()