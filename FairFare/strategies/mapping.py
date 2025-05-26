from FairFare.strategies.methods import even_split, exact_split, ratio_split

SPLIT_METHODS_MAPPING = {
    'even': even_split,
    'exact': exact_split,
    'ratio': ratio_split
}