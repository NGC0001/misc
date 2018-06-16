#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib, time, struct, sys


# Secret is base32 encoded, so should be decoded first.
# window determines the time offset.
def GoogleAuthenticator(secret, window = 0):
    secret = simple_base32_decode(secret)
    timeStamp = int(time.time()) + 30 * window
    return TOTP(secret, timeStamp)


def simple_base32_decode(code):
    base32LookUpTable = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', #/  7
        'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', #/ 15
        'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', #/ 23
        'Y', 'Z', '2', '3', '4', '5', '6', '7', #/ 31
        '='  #/ padding char
    ]
    base32DecodeDict = {}
    for i in range(len(base32LookUpTable)):
        base32DecodeDict[base32LookUpTable[i]] = i
    segments = []
    for i in range(len(code) / 8):
        segment40bit = 0
        for j in range(8):
            decoded = base32DecodeDict[code[i * 8 + 7 - j]]
            segment40bit += decoded << (j * 5)
        segments.append(segment40bit)
    decode = ''
    for i in range(len(segments)):
        str5byte = struct.pack('q', segments[i])[4::-1]
        decode += str5byte
    return decode


# Implementation of the TOTP algorithm.
# Time-based one-time password.
# K is the secret shared between client and server.
# unixTimeStamp is the UNIX time since 1970.1.1.
# Digit determines the length of returned string.
def TOTP(K, unixTimeStamp = None, Digit = 6):
    T0 = 0
    X = 30
    if unixTimeStamp == None:
        unixTimeStamp = int(time.time())
    T = (unixTimeStamp - T0) / X
    return HOTP(K, T, Digit = Digit)


# Implemetation of the HOTP algorithm.
# HAMC-based one-time password.
# K is the secret shared between client and server.
# C is the moving factor, and must be sychronized between the client and the server.
# Digit determines the length of returned string.
def HOTP(K, C, Digit = 6, Debug_HMAC_SHA_1_STR = None):
    if Debug_HMAC_SHA_1_STR == None:
        HMAC_SHA_1_STR = HMAC_SHA_1(K, C)
    else:
        HMAC_SHA_1_STR = Debug_HMAC_SHA_1_STR
    returnDigit = truncate(HMAC_SHA_1_STR, Digit = Digit)
    returnStr = str(returnDigit)
    while len(returnStr) < Digit:
        returnStr = '0' + returnStr
    return returnStr


# Truncate function used by HOTP algorithm.
# hashString should be a 20-byte string.
def truncate(hashString, Digit = 6):
    Snum = DT(hashString)  # Sbits is a 31-bit string
    return Snum % (10 ** Digit)


# DT function used by truncate algorithm.
# String should be a 20-byte string.
def DT(String):
    byteArr = struct.unpack('B' * len(String), String)
    offset = byteArr[19] & 15
    P = 0
    P = P | ((byteArr[offset] & 127) << 24)
    P = P | (byteArr[offset + 1] << 16)
    P = P | (byteArr[offset + 2] << 8)
    P = P | byteArr[offset + 3]
    return P


# C will be converted to a 8-byte counter value.
# higher order bits of C is placed into lower index of text.
# text is a 8-byte stream.
def HMAC_SHA_1(K, C):
    textLen = 8
    text = []
    for i in range(textLen):
        text.append((C >> ((textLen - 1 - i) * 8)) & 0xff)
    text = struct.pack('B' * textLen, *tuple(text))
    return HMAC(hashlib.sha1, K, text).digest()


def HMAC(H, K, text):
    B = 64  # Byte-length for hash blocks.
    if len(K) > B:
        K = H(K).digest()
    ipad = 0x36
    opad = 0x5c
    while len(K) < B:
        K = K + '\x00'
    KArr = struct.unpack('B' * B, K)
    iKArr = []
    for i in range(64):
        iKArr.append(KArr[i] ^ ipad)
    iK = struct.pack('B' * B, *tuple(iKArr))
    oKArr = []
    for i in range(64):
        oKArr.append(KArr[i] ^ opad)
    oK = struct.pack('B' * B, *tuple(oKArr))
    return H(oK + H(iK + text).digest())


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        secret = sys.argv[1]
        window = 0
        if len(sys.argv) >= 3:
            window = int(sys.argv[2])
        print GoogleAuthenticator(secret, window)

