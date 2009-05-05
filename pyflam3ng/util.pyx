import numpy as np
cimport numpy as np
import random as rn


def fast_improve(np.ndarray[ndim=1, dtype=np.uint8_t] orig, int ntries,\
                     int trysize):
          cdef np.ndarray[ndim=1, dtype=np.uint8_t] best = orig.copy()
          cdef np.ndarray[ndim=1, dtype=np.uint8_t] pal
          cdef int best_len = get_length(best)
          cdef int j, i, i0, i1, as_is, swapd, pal_len
          for i in range(ntries):
                    pal = best.copy()
                    for j in range(0, 768, 3):
                              pix_swap(pal, j, rn.randint(0, 255)*3)
                    pal_len = get_length(pal)
                    for j in range(trysize):
                              i0 = (1 + rn.randint(0,253))*3
                              i1 = (1 + rn.randint(0,253))*3
                              if i0-i1==3:
                                        as_is = (pix_diff(pal, i1-3, i1) +
                                                pix_diff(pal, i0, i0+3))
                                        swapd = (pix_diff(pal, i1-3, i0) +
                                                pix_diff(pal, i0, i1+3))
                              elif i1-i0==3:
                                        as_is = (pix_diff(pal, i0-3, i0) +
                                              pix_diff(pal, i1, i1+3))
                                        swapd = (pix_diff(pal, i0-3, i1) +
                                                pix_diff(pal, i1, i0+3))
                              else:
                                        as_is = (pix_diff(pal, i0, i0+3) +
                                                pix_diff(pal, i0, i0-3) +
                                                pix_diff(pal, i1, i1+3) +
                                                pix_diff(pal, i1, i1-3))
                                        swapd = (pix_diff(pal, i1, i0+3) +
                                                pix_diff(pal, i1, i0-3) +
                                                pix_diff(pal, i0, i1+3) +
                                                pix_diff(pal, i0, i1-3))
                              if swapd < as_is:
                                        pix_swap(pal, i0, i1)
                                        pal_len += (swapd - as_is)
                                  #end trysize loop
                    if pal_len < best_len:
                              best = pal.copy()
                              best_len = pal_len
                    #end ntries loop
          for i in xrange(256):
                    i0 = (1 + rn.randint(0, 252))*3
                    i1 = i0 + 3
                    as_is = (pix_diff(best, i0-3, i0) +
                              pix_diff(best, i1, i1+3))
                    swapd = (pix_diff(best, i0-3, i1) +
                              pix_diff(best, i0, i1+3))
                    if swapd < as_is:
                            pix_swap(best, i0, i1)
          return best

def get_length(np.ndarray[ndim=1, dtype=np.uint8_t] pal):
          cdef int length = 0
          cdef int i
          for i in range(3,756,3):
                    length += pix_diff(pal, i, i-3)
          return length

def pix_diff(np.ndarray[ndim=1, dtype=np.uint8_t] pal, int i0, int i1):
          cdef int diff = 0
          cdef int i
          for i in range(3):
                    diff += (pal[i0+i] - pal[i1+i])**2
          return diff

def pix_swap(np.ndarray[ndim=1, dtype=np.uint8_t] pal, int i0, int i1):
          cdef int i
          cdef unsigned char tmp
          for i in range(3):
                    tmp = pal[i0+i]
                    pal[i0+i] = pal[i1+i]
                    pal[i1+i] = tmp
