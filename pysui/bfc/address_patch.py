# -*- coding: utf-8 -*-

"""Sui / BFC address conversion."""

import re, hashlib


def valid_bfc_address(bfc_addr: str) -> bool:
    if re.match(r"^BFC[a-fA-F0-9]{64}[a-fA-F0-9]{4}$", bfc_addr):
        payload = bfc_addr[3:67].lower()
        h = hashlib.sha256()
        h.update(payload.encode("utf-8"))
        return h.hexdigest()[:4] == bfc_addr[67:71].lower()
    return False


def address_bfc_to_sui(bfc_addr: str) -> str:
    if re.match(r"^BFC[a-fA-F0-9]{64}[a-fA-F0-9]{4}$", bfc_addr):
        return "0x" + bfc_addr[3:67]
    raise ValueError(f"invalid bfc address: {bfc_addr}")


def try_convert_to_sui_address(addr: str) -> str:
    """Try to convert address to bfc address. Return original address if not valid."""
    if valid_bfc_address(addr):
        return "0x" + addr[3:67]
    return addr


def try_convert_to_bfc_address(sui_addr: str) -> str:
    if re.match(r"^0[xX][a-fA-F0-9]{1,64}$", sui_addr):
        without0x = sui_addr[2:]
        padding = 64 - len(without0x)
        if padding > 0:
            without0x = "0" * padding + without0x
        h = hashlib.sha256()
        h.update(without0x.encode("utf-8"))
        return "BFC" + without0x + h.hexdigest()[:4]
    return None
