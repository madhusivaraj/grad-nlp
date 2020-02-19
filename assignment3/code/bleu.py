import math
import sys

from collections import Counter
from functools import reduce


def compute_bleu(reflists, hyps, n_max=4, use_shortest_ref=False):
    assert len(reflists) == len(hyps)

    prec_mean = 0  # TODO: Implement
    brevity_penalty = 0  # TODO:Implement
    bleu = brevity_penalty * prec_mean

    return bleu


def get_ngram_counts(refs, hyp, n):
    hyp_ngrams = [tuple(hyp[i:i + n]) for i in range(len(hyp) - n + 1)]
    num_hyp_ngrams = max(1, len(hyp_ngrams))  # Avoid empty

    num_hyp_ngrams_in_refs_clipped = 0  # TODO: Implement

    return num_hyp_ngrams_in_refs_clipped, num_hyp_ngrams
