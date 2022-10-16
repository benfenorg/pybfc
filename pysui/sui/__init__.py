"""Provides version checking and export the Configuration."""
import sys

from sui.sui_constants import *
from sui.sui_excepts import SuiInvalidAddress
from sui.sui_apidesc import SuiApi, build_api_descriptors
from sui.sui_builders import (
    SuiBaseBuilder,
    GetObjectsOwnedByAddress,
    GetObject,
    GetObjectsOwnedByObject,
    GetRawPackage,
    GetPackage,
    GetRpcAPI,
    TransferSui,
    Pay,
    ExecuteTransaction,
    SuiRequestType,
)
from sui.sui_config import SuiConfig
from sui.sui_rpc import SuiClient, SuiRpcResult
from sui.sui_types import *
from sui.sui_crypto import keypair_from_keystring
from sui.sui_txn_validator import validate_api, valid_sui_address

if sys.version_info < (3, 10):
    raise EnvironmentError("Python 3.10 or above is required")