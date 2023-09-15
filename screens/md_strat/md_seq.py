from statistics             import mean, stdev
from sys                    import argv, path

path.append(".")

from typing                 import List
from util.bar_tools         import bar_rec
from util.contract_settings import get_settings
from util.pricing           import call, call_vertical, fly, iron_fly, put, put_vertical, straddle
from util.rec_tools         import get_precision

# python screens/md_strat/md_seq.py


if __name__ == "__main__":

    pass