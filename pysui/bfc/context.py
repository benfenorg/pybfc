# -*- coding: utf-8 -*-

""" activate_bfc() to use BFC if connected to BFC network."""

__use_bfc = False


def activate_bfc():
    global __use_bfc
    __use_bfc = True
    print("BFC was activated.")


def is_bfc_activated():
    return __use_bfc
