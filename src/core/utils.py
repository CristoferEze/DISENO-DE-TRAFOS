# src/core/utils.py
# -*- coding: utf-8 -*-

def get_promedio(v):
    return (v[0] + v[1]) / 2

def sel_clave(d, val):
    return min([k for k in d if k >= val] or [max(d)])

def f_dec(v):
    return "{:.2f}".format(v)

def f_int(v):
    return "{}".format(int(v))