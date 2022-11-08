#    Copyright 2022 Frank V. Castellucci
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# -*- coding: utf-8 -*-


"""Argument parsing."""
import argparse
import sys
from pathlib import Path
from typing import Any, Sequence
from pysui.sui.sui_types import ObjectID, SuiNumber, SuiAddress, SuiString


def check_positive(value: str) -> int:
    """Check for positive integers."""
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return SuiNumber(ivalue)


class ValidateAddress(argparse.Action):
    """Address validator."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = ...,
    ) -> None:
        """Validate."""
        try:
            if isinstance(values, list):
                values = [SuiAddress.from_hex_string(v) for v in values]
            else:
                values = SuiAddress.from_hex_string(values)
        except ValueError:
            parser.error(f"'{values}' is not valid address.")
            sys.exit(-1)
        setattr(namespace, self.dest, values)


class ValidateObjectID(argparse.Action):
    """ObjectID validator."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = ...,
    ) -> None:
        """Validate."""
        try:
            if isinstance(values, list):
                values = [ObjectID(v) for v in values]
            else:
                values = ObjectID(values)
        except ValueError:
            parser.error(f"'{values}' is not valid address.")
        setattr(namespace, self.dest, values)


class ValidatePackageDir(argparse.Action):
    """Validate package directory."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = ...,
    ) -> None:
        """Validate."""
        ppath = Path(values)
        if not ppath.exists:
            parser.error(f"{str(ppath)} does not exist.")
        setattr(namespace, self.dest, ppath)


def _build_read_cmds(subparser) -> None:
    """Read commands."""
    # Address
    subp = subparser.add_parser("active-address", help="Shows active address")
    subp.set_defaults(subcommand="active-address")
    # Addresses
    subp = subparser.add_parser("addresses", help="Shows all addresses")
    subp.set_defaults(subcommand="addresses")
    # New address
    subp = subparser.add_parser("new-address", help="Generate new address and keypair")
    addy_arg_group = subp.add_mutually_exclusive_group(required=True)
    addy_arg_group.add_argument("-e", "--ed25519", help="Generate using ed25519 scheme", action="store_true")
    addy_arg_group.add_argument("-s", "--secp256k1", help="Generate using secp256k1 scheme", action="store_true")
    subp.set_defaults(subcommand="new-address")
    # Switch address
    # subp = subparser.add_parser("switch", help="Change the active address")
    # subp.add_argument("-a", "--address", required=True, help="Address to change to", action=ValidateAddress)
    # subp.set_defaults(subcommand="switch")
    # Gas
    subp = subparser.add_parser("gas", help="Shows gas objects and total mist")
    subp.add_argument("-a", "--address", required=False, help="Gas for address", action=ValidateAddress)
    subp.set_defaults(subcommand="gas")
    # Object
    subp = subparser.add_parser("object", help="Show object by id")
    subp.add_argument("--id", required=True, action=ValidateObjectID)
    subp.add_argument("--json", required=False, help="Display output as json", action="store_true")
    subp.set_defaults(subcommand="object")
    # Objects
    subp = subparser.add_parser("objects", help="Show all objects")
    subp.add_argument("-a", "--address", required=False, help="Objects for address", action=ValidateAddress)
    subp.add_argument("-j", "--json", required=False, help="Display output as json", action="store_true")
    obj_arg_group = subp.add_mutually_exclusive_group()
    obj_arg_group.add_argument("-n", "--nft", help="Only show NFT objects", action="store_true")
    obj_arg_group.add_argument("-d", "--data", help="Only show data objects", action="store_true")
    subp.set_defaults(subcommand="objects")
    # RPC information
    subp = subparser.add_parser("rpcapi", help="Show Sui RPC API information")
    subp.add_argument("-n", "--name", required=False, help="Display details for named Sui RPC API")
    subp.set_defaults(subcommand="rpcapi")
    # Committee info
    subp = subparser.add_parser("committee", help="Show committee info for epoch")
    subp.add_argument(
        "-e",
        "--epoch",
        required=False,
        help="The epoch of interest. If None, default to the latest epoch",
        type=check_positive,
    )
    subp.set_defaults(subcommand="committee")


def _build_transfer_cmds(subparser) -> None:
    """Transfer commands."""
    # Transfer SUI
    subp = subparser.add_parser("transfer-object", help="Transfer an object from one address to another")
    subp.add_argument(
        "-d",
        "--object-id",
        required=True,
        help="Specify sui object being transfered",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-o",
        "--gas",
        required=True,
        help="Specify sui gas object paying for the transaction",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-r",
        "--recipient",
        required=True,
        help="Specify recipient address to send object to",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'transfer-object' transaction budget amount in mists (e.g. 1000)",
        type=check_positive,
    )
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify gas owner address for signing. Default to active address",
        action=ValidateAddress,
    )
    subp.set_defaults(subcommand="transfer-object")
    # Transfer SUI
    subp = subparser.add_parser("transfer-sui", help="Transfer SUI 'mist(s)' to a Sui address")
    subp.add_argument(
        "-a",
        "--amount",
        required=True,
        help="Specify amount of MISTs to transfer.",
        type=check_positive,
    )
    subp.add_argument(
        "-o",
        "--sui-object-id",
        required=True,
        help="Specify sui gas object to transfer from",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-r",
        "--recipient",
        required=True,
        help="Specify recipient wallet address to send SUI Mists to",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'transfer-sui' transaction budget amount in Mist (e.g. 1000)",
        type=check_positive,
    )
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify gas owner address for signing. Default to active address",
        action=ValidateAddress,
    )
    subp.set_defaults(subcommand="transfer-sui")


def _build_pay_cmds(subparser) -> None:
    """Pay commands."""
    # Pay
    subp = subparser.add_parser("pay", help="Send coin of any type to recipient(s)")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify pay signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-i",
        "--input-coins",
        required=True,
        nargs="+",
        help="Specify the input coins for each <RECEIPIENT>:<AMOUNTS> to send to",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-a",
        "--amounts",
        required=True,
        nargs="+",
        help="Specify amounts of MIST for each <INPUT-COINS> provided.",
        type=check_positive,
    )
    subp.add_argument(
        "-r",
        "--recipients",
        required=True,
        nargs="+",
        help="Specify recipient address for each <AMOUNTS>:<INPUT-COINS> to send to",
        action=ValidateAddress,
    )
    subp.add_argument("-o", "--gas", required=True, help="Specify gas object to transfer from", action=ValidateObjectID)
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'pay' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="pay")
    # PaySui
    subp = subparser.add_parser("paysui", help="Send SUI coins to a list of addresses.")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify pay signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-i",
        "--input-coins",
        required=True,
        nargs="+",
        help="Specify the input sui coins for each <RECEIPIENT>:<AMOUNTS> to send to",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-a",
        "--amounts",
        required=True,
        nargs="+",
        help="Specify amounts of MIST for each <INPUT-COINS> provided.",
        type=check_positive,
    )
    subp.add_argument(
        "-r",
        "--recipients",
        required=True,
        nargs="+",
        help="Specify recipient address for each <AMOUNTS>:<INPUT-COINS> to send to",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'pay' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="paysui")
    # PayAllSui
    subp = subparser.add_parser("payallsui", help="Send all SUI coin(s) to recipient(s)")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify pay signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-i",
        "--input-coins",
        required=True,
        nargs="+",
        help="Specify the sui coins to use, including transaction payment",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-r",
        "--recipient",
        required=True,
        help="Specify recipient address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'pay' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="payallsui")


def _build_package_cmds(subparser) -> None:
    """Package commands."""
    # Package Object
    subp = subparser.add_parser("package-object", help="Show raw package object with Move disassembly")
    subp.add_argument("-i", "--id", required=True, help="package ID", action=ValidateObjectID)
    subp.add_argument("-s", "--src", required=False, help="Display package module(s) src", action="store_true")
    subp.set_defaults(subcommand="package-object")
    # Normalized Package
    subp = subparser.add_parser("package", help="Show normalized package information")
    subp.add_argument("-i", "--id", required=True, help="package ID", action=ValidateObjectID)
    subp.set_defaults(subcommand="package")
    # Publish package
    subp = subparser.add_parser("publish", help="Publish a SUI package")
    subp.add_argument(
        "-s",
        "--sender",
        required=False,
        help="Specify publish sender address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-c",
        "--compiled_modules",
        required=True,
        help="Specify the path to package folder containing compiled modules to publish.",
        action=ValidatePackageDir,
    )
    subp.add_argument(
        "-o", "--gas", required=True, help="Specify gas object to pay transaction from", action=ValidateObjectID
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'split-coin' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="publish")
    # Move call
    subp = subparser.add_parser("call", help="Call a move contract function")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify split-coin signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-p",
        "--package",
        required=True,
        help="Specify the package ID owner of the move module and function.",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-m",
        "--module",
        required=True,
        help="Specify the module name in the package.",
        type=SuiString,
    )
    subp.add_argument(
        "-f",
        "--function",
        required=True,
        help="Specify the function name in the module.",
        type=SuiString,
    )
    subp.add_argument(
        "-t",
        "--types",
        required=False,
        nargs="+",
        help="Generic types (if any).",
        type=SuiString,
    )
    subp.add_argument(
        "-a",
        "--arguments",
        required=False,
        nargs="+",
        help="Function arguments.",
        type=SuiString,
    )
    subp.add_argument(
        "-o", "--gas-object", required=True, help="Specify gas object to pay transaction from", action=ValidateObjectID
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'split-coin' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="call")


def _build_coin_cmds(subparser) -> None:
    """Coin commands."""
    # Merge coin
    subp = subparser.add_parser("merge-coin", help="Merge two coins together")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify merge-coin signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-p",
        "--primary-coin",
        required=True,
        help="Specify the primary coin ID to merge into",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-c",
        "--coin-to-merge",
        required=True,
        help="Specify the coin ID to merge from.",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-o", "--gas-object", required=True, help="Specify gas object to pay transaction from", action=ValidateObjectID
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'merge-coin' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="merge-coin")
    # Split coin
    subp = subparser.add_parser("split-coin", help="Split coin into one or more coins")
    subp.add_argument(
        "-s",
        "--signer",
        required=False,
        help="Specify split-coin signer address. Default to active address",
        action=ValidateAddress,
    )
    subp.add_argument(
        "-c",
        "--coin_object_id",
        required=True,
        help="Specify the coin ID the split-amounts are being split from.",
        action=ValidateObjectID,
    )
    subp.add_argument(
        "-a",
        "--split_amounts",
        required=True,
        nargs="+",
        help="Specify amounts to split the coin into.",
        type=check_positive,
    )
    subp.add_argument(
        "-o", "--gas-object", required=True, help="Specify gas object to pay transaction from", action=ValidateObjectID
    )
    subp.add_argument(
        "-g",
        "--gas-budget",
        required=True,
        help="Specify 'split-coin' transaction budget",
        type=check_positive,
    )
    subp.set_defaults(subcommand="split-coin")


def _build_extended_read_commands(subparser) -> None:
    """More Object read commands."""

    def __common_event_opts(eparser) -> None:
        eparser.add_argument("-c", "--count", required=True, help="maximum number of the results", type=check_positive)
        eparser.add_argument(
            "-s", "--start_time", required=True, help="left endpoint of time interval, inclusive", type=check_positive
        )
        eparser.add_argument(
            "-e", "--end_time", required=True, help="right endpoint of time interval, exclusive", type=check_positive
        )

    # Events
    subp = subparser.add_parser(
        "events", help="Show events for types", usage="events subcommand [--subcommand_options]"
    )
    ecmds = subp.add_subparsers(title="subcommand", required=True)
    # Module events
    esubp = ecmds.add_parser("module", help="Return events emitted in a specified Move module")
    esubp.add_argument("-p", "--package", required=True, help="the SUI package ID", action=ValidateObjectID)
    esubp.add_argument("-m", "--module", required=True, help="the module name", type=str)
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-module")
    # Structure events
    esubp = ecmds.add_parser("struct", help="Return events with the given move event struct name")
    esubp.add_argument("-n", "--name", required=True, dest="move_event_struct_name", type=str)
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-struct")
    # Object events
    esubp = ecmds.add_parser("object", help="Return events associated with the given object")
    esubp.add_argument("-o", "--object", required=True, help="the SUI object ID", action=ValidateObjectID)
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-object")
    # Recipient events
    esubp = ecmds.add_parser("recipient", help="Return events associated with the given recipient")
    esubp.add_argument("-r", "--recipient", required=True, help="the SUI address of recipient", type=str)
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-recipient")
    # Sender events
    esubp = ecmds.add_parser("sender", help="Return events associated with the given sender")
    esubp.add_argument(
        "-a", "--address", required=True, dest="sender", help="the SUI address of sender", action=ValidateAddress
    )
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-sender")
    # Time events
    esubp = ecmds.add_parser("time", help="Return events emitted in [start_time, end_time) interval")
    __common_event_opts(esubp)
    esubp.set_defaults(subcommand="event-time")
    esubp = ecmds.add_parser("transaction", help="Return events emitted by the given transaction")
    esubp.add_argument("-d", "--digest", required=True, help="the transaction's digest")
    esubp.add_argument("-c", "--count", required=True, help="maximum number of the results", type=check_positive)
    esubp.set_defaults(subcommand="event-tx")


def _build_tx_query_commands(subparser) -> None:
    """Transaction information read commands."""
    # Transactions
    subp = subparser.add_parser(
        "txns", help="Show transaction information", usage="txns subcommand [--subcommand_options]"
    )
    tcmds = subp.add_subparsers(title="subcommand", required=True)
    # Total count
    esubp = tcmds.add_parser("count", help="Return total transaction count from server")
    esubp.set_defaults(subcommand="txn-count")
    # Transaction
    esubp = tcmds.add_parser("txn", help="Return transaction information")
    esubp.add_argument("-d", "--digest", required=True, help="the transaction's digest")
    esubp.set_defaults(subcommand="txn-txn")


def build_parser(in_args: list) -> argparse.Namespace:
    """Build the argument parser structure."""
    # Base menu
    parser = argparse.ArgumentParser(add_help=True, usage="%(prog)s [options] command [--command_options]")
    subparser = parser.add_subparsers(title="commands")
    _build_read_cmds(subparser)
    _build_coin_cmds(subparser)
    _build_transfer_cmds(subparser)
    _build_pay_cmds(subparser)
    _build_package_cmds(subparser)
    # _build_extended_read_commands(subparser)
    _build_tx_query_commands(subparser)

    return parser.parse_args(in_args if in_args else ["--help"])
