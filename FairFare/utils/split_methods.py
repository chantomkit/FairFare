from typing import Dict


def even_split(total: float, input_participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Evenly split `total` among `participants`.
    :param total: Total amount to be split.
    :param input_participant_shares: Mapping from participant id to share.
    :return: Mapping from participant id to owed share amounts.
    """
    per_head = total / len(input_participant_shares)
    return {pid: per_head for pid in input_participant_shares.keys()}


def exact_split(total: float, input_participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Split `total` according to shares provided in `input_participant_shares`.
    :param total: Total amount to be split.
    :param input_participant_shares: Mapping participant id to their share.
    :return: Mapping from participant id to owed share amounts.
    """
    print(total, input_participant_shares, sum(input_participant_shares.values()))

    if not all(share is not None for share in input_participant_shares.values()):
        raise ValueError("Exact shares must be provided for all participants.")

    if abs(sum(input_participant_shares.values()) - total) > 1e-9:
        raise ValueError("Exact shares must sum to the total payment amount.")

    return input_participant_shares


def ratio_split(total: float, input_participant_shares: Dict[str, float]) -> Dict[str, float]:
    """
    Split `total` according to the ratio in `input_participant_shares`.
    :param total: Total amount to be split.
    :param input_participant_shares: Mapping from participant id to ratio.
    :return: Mapping from participant id to owed share amounts.
    """
    if not all(0 <= share <= 1 for share in input_participant_shares.values()):
        raise ValueError("Share ratios must be between 0 and 1 (inclusive).")

    if abs(sum(input_participant_shares.values()) - 1.0) > 1e-9:
        raise ValueError("Total ratio must equal 1.")

    return {pid: total * share for pid, share in input_participant_shares.items()}
