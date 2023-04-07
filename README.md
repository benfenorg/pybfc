<img src="https://raw.githubusercontent.com/FrankC01/pysui/main/images//pysui_logo_color.png" width="150" height="200"/>

# pysui

Python Client SDK for Sui blockchain

## **NOTICE: README FIRST**

**Release-0.16.0 - IN REPO ONLY**

This release introduces **MultiSig** (multiple keyt signing) for extra security governance! A section in the online
documentation has been added to describe the basics.

This release introduces **Programmable Transactions** See `pysui/sui/sui_client/transaction.py` It is still being worked
and contains too much code, asserts,TODO and FIXME. Note\_ that the legacy Builders and ease of use API on SuiClient are still available.

We would appreciate any issues being reported in the [github issue log](https://github.com/FrankC01/pysui/issues)

This is a _**beta**_ release. The degree of changes from 0.27.1 to 0.29.1 are such that we have not completed thorough testing. We wanted to get something out there for users who have moved to 0.29.x devnet or testinet.

The amount of changes have eviscerated the pytest implementations and should not be trusted at this time.

Sui release 0.29.x brings **_significant_** breaking changes. Please read the CHANGLOG first as many builders and data models have changed or even been removed. Refer to the [Changes](https://github.com/FrankC01/pysui/blob/main/CHANGELOG.md) log for recent additions, changes, constraints, fixes and removals...

- 100% coverage (builders, return types, etc.) for parity with _SUI 0.29.0 API_ on devnet (see Testnet below)
  - Programmable Transactions not yet supported. We are working on a TransactionBuilder and should have this available soon.

**PyPi for 0.15.0**

- [Latest PyPi Version](https://pypi.org/project/pysui/)

## Connect with us!

We have a channel in the [sui-base](https://github.com/sui-base/sui-base) Discord server [click here](https://discord.com/invite/Erb6SwsVbH):

## Additions

There is a companion package called [pysui-gadgets](https://github.com/FrankC01/pysui_gadgets) with a few utilities and ge-gaws that
you may find interesting. It is a separate package also on on PyPi.

## Documentation

- [ReadTheDocs](https://pysui.readthedocs.io/en/latest/index.html)

## Ready to run

Requires:

- Linux or macos (x86_64 or M1)
- python 3.10 or greater
- pkg-config
- sui binaries to support `publish` function

### Setup environment

`python3 -m venv env`

If, instead, you want to work with repo latest source code then read [DEVELOP](https://github.com/FrankC01/pysui/blob/main/DEVELOP.md) from repo

### Activate

`source env/bin/activate`

or

`. env/bin/activate`

### Install `pysui`

`pip install --use-pep517 pysui`

## Samples

See [samples](https://github.com/FrankC01/pysui/blob/main/samples/README.md)
