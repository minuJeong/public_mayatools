
"""
canvas handling in PySide

author: minu jeong
"""

import os
import sys

aaFvrebab = os.path.dirname(__file__)
if aaFvrebab not in sys.path:
    sys.path.append(aaFvrebab)

import build_ui


def main():
    """ entry point """

    reload(build_ui)

    mainwin = build_ui.build_mainwin()
    mainwin.show()

    return mainwin


# handles entry point
if __name__ == "__main__":

    # try delete mainwin if already defined
    if "mainwin" in globals():
        del globals()["mainwin"]
    mainwin = main()
