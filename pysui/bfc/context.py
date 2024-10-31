# -*- coding: utf-8 -*-

""" activate_bfc() to use BFC if connected to BFC network."""

__use_bfc = False


def activate_bfc(active=True):
    global __use_bfc
    __use_bfc = active
    if active:
        print("BFC was activated.")
    else:
        print("BFC was deactivated.")


def is_bfc_activated():
    return __use_bfc
