# -*- coding: utf-8 -*-

"""Sui / BFC rpc patch."""


def to_bfc_rpc_method(method: str) -> str:
    if method.startswith("suix_"):
        return "bfcx_" + method[5:]
    if method.startswith("sui_"):
        return "bfc_" + method[4:]
    return method


def to_sui_rpc_method(method: str) -> str:
    if method.startswith("bfcx_"):
        return "suix_" + method[5:]
    if method.startswith("bfc_"):
        return "sui_" + method[4:]
    return method
