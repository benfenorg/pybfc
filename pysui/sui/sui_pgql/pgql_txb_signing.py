#    Copyright Frank V. Castellucci
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

"""Pysui Signing Block builder that works with GraphQL connection."""

import base64
from typing import Optional, Union
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_pgql.pgql_clients import BaseSuiGQLClient
from pysui.sui.sui_pgql.pgql_query import GetCoins
from pysui.sui.sui_types import bcs
import pysui.sui.sui_pgql.pgql_types as pgql_type
import pysui.sui.sui_pgql.pgql_query as qn
from pysui.sui.sui_crypto import MultiSig, BaseMultiSig, SuiPublicKey

import pysui.sui.sui_pgql.pgql_types as pgql_type


class SigningMultiSig:
    """Wraps the mutli-sig along with pubkeys to use in SuiTransaction."""

    def __init__(self, msig: BaseMultiSig, pub_keys: list[SuiPublicKey]):
        """."""
        self.multi_sig = msig
        self.pub_keys = pub_keys
        self.indicies = msig.validate_signers(pub_keys)
        self._address = self.multi_sig.address
        self._can_sign_msg = isinstance(msig, MultiSig)

    @property
    def signing_address(self) -> str:
        """."""
        return self._address


class _SignerBlockBase:
    """."""

    def __init__(
        self,
        *,
        sender: Optional[Union[str, SigningMultiSig]] = None,
        sponsor: Optional[Union[str, SigningMultiSig]] = None,
    ):
        """__init__ Create a signer block.

        :param sender: The primary sender/signer, defaults to None
        :type sender: Optional[Union[str, SigningMultiSig]], optional
        :param sponsor: An optional sponsor for transaction, defaults to None
        :type sponsor: Optional[Union[str, SigningMultiSig]], optional
        """
        self._sender = sender
        self._sponsor = sponsor
        self._merge_to_gas: bool = False

    @property
    def sender(self) -> Union[str, SigningMultiSig]:
        """Return the current sender used in signing."""
        return self._sender

    @property
    def sender_str(self) -> str:
        """Return the current sender used in signing."""
        return (
            self._sender
            if isinstance(self._sender, str)
            else self._sender.signing_address
        )

    @sender.setter
    def sender(self, new_sender: Union[str, SigningMultiSig]):
        """Set the sender to use in signing the transaction."""
        assert isinstance(new_sender, (str, SigningMultiSig))
        self._sender = new_sender

    @property
    def sponsor(self) -> Union[None, Union[str, SigningMultiSig]]:
        """Get who, if any, may be acting as payer of transaction."""
        return self._sponsor

    @property
    def sponsor_str(self) -> Union[str, None]:
        """Return the current sender used in signing."""
        if not self._sponsor:
            return None
        return (
            self._sponsor
            if isinstance(self._sponsor, str)
            else self._sponsor.signing_address
        )

    @sponsor.setter
    def sponsor(self, new_sponsor: Union[str, SigningMultiSig]):
        """Set the sponsor to used to pay for transaction. This also signs the transaction."""
        assert isinstance(new_sponsor, (str, SigningMultiSig))
        self._sponsor = new_sponsor

    def _get_potential_signatures(
        self,
    ) -> list[Union[str, SigningMultiSig]]:
        """Internal flattening of signers."""
        result_list = []
        if self.sender:
            result_list.append(self.sender)
        if self.sponsor:
            result_list.append(self._sponsor)
        return result_list

    def get_signatures(self, *, config: SuiConfig, tx_bytes: str) -> list[str]:
        """Get all the signatures needed for the transaction."""
        sig_list: list[str] = []
        for signer in self._get_potential_signatures():
            if isinstance(signer, str):
                sig_list.append(config.kp4add(signer).new_sign_secure(tx_bytes))
            else:
                if signer._can_sign_msg:
                    sig_list.append(signer.multi_sig.sign(tx_bytes, signer.pub_keys))
                else:
                    raise ValueError("BaseMultiSig can not sign in execution")
        return sig_list


class SignerBlock(_SignerBlockBase):
    """Manages the potential signers and resolving the gas object for paying."""

    def __init__(
        self,
        *,
        sender: Optional[Union[str, SigningMultiSig]] = None,
        sponsor: Optional[Union[str, SigningMultiSig]] = None,
    ):
        """__init__ Create a signer block.

        :param sender: The primary sender/signer, defaults to None
        :type sender: Optional[Union[str, SigningMultiSig]], optional
        :param sponsor: An optional sponsor for transaction, defaults to None
        :type sponsor: Optional[Union[str, SigningMultiSig]], optional
        """
        super().__init__(sender=sender, sponsor=sponsor)

    def _get_payer(self) -> Union[str, ValueError]:
        """Get the payer for the transaction."""
        # Either a sponsor (priority) or sender will pay for this
        who_pays = self._sponsor if self._sponsor else self._sender
        # If both not set, Fail
        if not who_pays:
            raise ValueError(
                "Both SuiTransaction sponor and sender are null. Complete at least one before execute."
            )
        if isinstance(who_pays, str):
            who_pays = who_pays
        else:
            who_pays = who_pays.signing_address

        return who_pays

    @property
    def payer_address(self) -> str:
        """Fetch payer address."""
        return self._get_payer()

    # TODO: GitHub #177
    def _get_gas_data(
        self,
        payer: str,
        owner_coins: list[pgql_type.SuiCoinObjectGQL],
        budget: int,
        objects_in_use: dict,
        merge_coin: bool,
        gas_price: int,
    ) -> Union[bcs.GasData, ValueError]:
        """Find the gas to pay for transaction."""
        # Scan for a single coin not in use that satisfies budget
        # but always accumulate and break if we meet threshold based on budget
        have_single = None
        owner_gas: list[pgql_type.ObjectReadGQL] = []
        threshold: int = 0
        for o_gas in owner_coins:
            # Eliminate any gas in use for commands
            if o_gas.object_id not in objects_in_use:
                # If the potential for one coin that satisfied budget exists
                if int(o_gas.balance) >= budget and not have_single:
                    have_single = o_gas
                owner_gas.append(o_gas)
                threshold += int(o_gas.balance)
                # If we have enough coins to satisfy budget
                if threshold >= budget:
                    break

        # If a merge_to_gas was part of transaction commands,
        # use the first object
        gas_data: list = None
        if self._merge_to_gas:
            use_coin = owner_coins[0]
            gas_data = [
                bcs.ObjectReference(
                    bcs.Address.from_str(use_coin.coin_object_id),
                    int(use_coin.version),
                    bcs.Digest.from_str(use_coin.digest),
                )
            ]

        # Otherwise, if we have one object that satisfies the budget
        elif have_single:
            gas_data = [
                bcs.ObjectReference(
                    bcs.Address.from_str(have_single.coin_object_id),
                    int(have_single.version),
                    bcs.Digest.from_str(have_single.digest),
                )
            ]
        # Else check that we meet the threshold
        elif threshold >= budget:
            # If we do and merge_gas_budget was specified on the SuiTransaction
            if merge_coin:
                gas_data = [
                    bcs.ObjectReference(
                        bcs.Address.from_str(x.object_id),
                        int(x.version),
                        bcs.Digest.from_str(x.digest),
                    )
                    for x in owner_gas
                ]
            else:
                raise ValueError(
                    f"{payer} has enough gas but merge_gas_budget not set on transaction."
                )

        else:
            raise ValueError(f"{payer} has nothing to pay with.")

        return bcs.GasData(
            gas_data,
            bcs.Address.from_str(payer),
            int(gas_price),
            int(budget),
        )

    def get_gas_object(
        self,
        *,
        client: BaseSuiGQLClient,
        budget: int,
        objects_in_use: dict,
        merge_coin: bool,
        gas_price: int,
    ) -> Union[bcs.GasData, ValueError]:
        """Produce a gas object from either the sponsor or the sender."""
        # Either a sponsor (priority) or sender will pay for this
        who_pays = self._get_payer()
        # Get current gas objects for payer
        gas_result = client.execute_query(
            # GetAllCoins defaults to "0x2::sui::SUI"
            with_query_node=GetCoins(owner=client.config.active_address.address)
        )
        if gas_result.is_ok():
            owner_coins: list[pgql_type.SuiCoinObjectGQL] = gas_result.result_data.data
        else:
            raise ValueError(
                f"Error {gas_result.result_string} attemepting to fetch gas objects for {who_pays}"
            )
        return self._get_gas_data(
            who_pays,
            owner_coins,
            budget,
            objects_in_use,
            merge_coin,
            gas_price,
        )

    def _get_gas_objects(
        self, client: BaseSuiGQLClient, gas_ids: list[str]
    ) -> list[pgql_type.SuiCoinObjectGQL]:
        """."""

    def _get_all_gas_objects(
        self, client: BaseSuiGQLClient
    ) -> list[pgql_type.SuiCoinObjectGQL]:
        """."""
        payer = self.payer_address
        coin_list: list[pgql_type.SuiCoinObjectGQL] = []
        result = client.execute_query(with_query_node=qn.GetCoins(owner=payer))
        while True:
            if result.is_ok():
                coin_list.extend(result.result_data.data)
                if result.result_data.next_cursor.hasNextPage:
                    result = client.execute_query(
                        with_query_node=qn.GetCoins(
                            owner=payer, next_page=result.result_data.next_cursor
                        )
                    )
                else:
                    break
            else:
                break
        return coin_list

    def _dry_run_for_budget(
        self,
        client: BaseSuiGQLClient,
        tx_bytes: str,
        active_gas_price: int,
    ) -> int:
        """."""
        result = client.execute_query(
            with_query_node=qn.DryRunTransactionKind(
                tx_bytestr=tx_bytes,
                tx_meta={
                    "sender": self.sender_str,
                    "gasPrice": active_gas_price,
                    "gasSponsor": self.sponsor_str,
                },
                skip_checks=False,
            )
        )
        if result.is_ok():
            if result.result_data.transaction_block.effects["status"] == "SUCCESS":
                c_cost: int = int(
                    result.result_data.transaction_block.effects["gasEffects"][
                        "gasSummary"
                    ]["computationCost"]
                )
                s_cost: int = int(
                    result.result_data.transaction_block.effects["gasEffects"][
                        "gasSummary"
                    ]["storageCost"]
                )
                return c_cost + s_cost
            else:
                raise ValueError(f"{result.result_data.errors}")
        else:
            raise ValueError(
                f"Error running DryRunTransactionBlock: {result.result_string}"
            )

    def get_gas_data(
        self,
        *,
        client: BaseSuiGQLClient,
        budget: Optional[int] = None,
        use_coins: Optional[list[Union[str, pgql_type.SuiCoinObjectGQL]]] = None,
        objects_in_use: set[str],
        active_gas_price: int,
        tx_kind: bcs.TransactionKind,
    ):
        """."""
        # Get available coins
        _specified_coins = True if use_coins else False
        if use_coins:
            if all(isinstance(x, str) for x in use_coins):
                use_coins = self._get_gas_objects(use_coins)
            elif not all(isinstance(x, pgql_type.SuiCoinObjectGQL) for x in use_coins):
                raise ValueError("use_gas_objects must use same type.")
        else:
            use_coins = self._get_all_gas_objects(client)
        if not budget:
            budget = self._dry_run_for_budget(
                client,
                base64.b64encode(tx_kind.serialize()).decode(),
                active_gas_price,
            )
        # Remove conflicts with objects in use
        use_coins = [x for x in use_coins if x.coin_object_id not in objects_in_use]
        # Make sure something left to pay for
        if use_coins:
            return budget, use_coins
        raise ValueError("No coin objects found to fund transaction.")
