from FairFare.utils.settle_methods import greedy_settlement
from FairFare.utils.split_methods import even_split, exact_split, ratio_split

SPLIT_METHODS_MAPPING = {
    "even": even_split,
    "exact": exact_split,
    "ratio": ratio_split,
}


SETTLEMENT_METHODS_MAPPING = {"greedy": greedy_settlement}
