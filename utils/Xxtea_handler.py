"""
-*- coding: utf-8 -*-
@Time : 2023/2/2 
@Author : liuyan
@function : 
"""

import struct

class Xxtea(object):
    _DELTA = 0x9E3779B9

    def _long2str(self, v, w):
        n = (len(v) - 1) << 2
        if w:
            m = v[-1]
            if (m < n - 3) or (m > n): return ''
            n = m
        s = struct.pack('<%iL' % len(v), *v)
        return s[0:n] if w else s

    def _str2long(self, s, w):
        n = len(s)
        m = (4 - (n & 3) & 3) + n
        s = s.ljust(m, b'\0')
        v = list(struct.unpack('<%iL' % (m >> 2), s))
        if w:
            v.append(n)
        return v

    def encrypt(self, str, key):
        if str == '': return str
        v = self._str2long(str, True)
        k = self._str2long(key.ljust(16, b'\0'), False)
        n = len(v) - 1
        z = v[n]
        y = v[0]
        sum = 0
        q = 6 + 52 // (n + 1)
        while q > 0:
            sum = (sum + self._DELTA) & 0xffffffff
            e = sum >> 2 & 3
            for p in xrange(n):
                y = v[p + 1]
                v[p] = (v[p] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff
                z = v[p]
            y = v[0]
            v[n] = (v[n] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[n & 3 ^ e] ^ z))) & 0xffffffff
            z = v[n]
            q -= 1
        return self._long2str(v, False)

    def decrypt(self, str, key):
        if str == '':
            return str
        v = self._str2long(str, False)
        # k = _str2long(key.ljust(16, b'\0'), False)
        k = self._str2long(key, False)
        n = len(v) - 1
        z = v[n]
        y = v[0]
        q = 6 + 52 // (n + 1)
        sum = (q * self._DELTA) & 0xffffffff
        while (sum != 0):
            e = sum >> 2 & 3
            for p in range(n, 0, -1):
                z = v[p - 1]
                v[p] = (v[p] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff
                y = v[p]
            z = v[n]
            v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[0 & 3 ^ e] ^ z))) & 0xffffffff
            y = v[0]
            sum = (sum - self._DELTA) & 0xffffffff
        return self._long2str(v, True)






