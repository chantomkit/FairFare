from typing import Dict
import numpy as np

def even_split(total: float, participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Evenly split `total` among `participants`.
    :param total: Total amount to be split.
    :param participant_shares: Mapping from participant id to their share.
    :return: Mapping from participant id to owed share amounts.
    """
    per_head = total / len(participant_shares)
    return {pid: per_head for pid in participant_shares.keys()}

def exact_split(total: float, participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Split `total` according to exact shares provided in `participant_shares`.
    :param total: Total amount to be split.
    :param participant_shares: Mapping from participant id to their exact share.
    :return: Mapping from participant id to owed share amounts.
    """
    print(total, participant_shares, sum(participant_shares.values()))
    
    if not all(share is not None for share in participant_shares.values()):
        raise ValueError("Exact shares must be provided for all participants.")
    
    if not np.allclose(sum(participant_shares.values()), total, atol=1e-2):
        raise ValueError("Exact shares must sum to the total payment amount.")
    
    return participant_shares

def ratio_split(total: float, participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Split `total` according to the ratio of shares provided in `participant_shares`.
    :param total: Total amount to be split.
    :param participant_shares: Mapping from participant id to their share ratio <= 1.
    :return: Mapping from participant id to owed share amounts.
    """    
    if not all(0 <= share <= 1 for share in participant_shares.values()):
        raise ValueError("Share ratios must be between 0 and 1 (inclusive).")

    if not np.allclose(sum(participant_shares.values()), 1.0, atol=1e-2):
        raise ValueError("Total ratio must equal 1.")
    
    return {pid: total * share for pid, share in participant_shares.items()}