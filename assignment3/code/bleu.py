import math
import sys

import collections
from collections import Counter
from functools import reduce


def compute_bleu(reflists, hyps, n_max=4, use_shortest_ref=False):
    assert len(reflists) == len(hyps)

    prec_mean = 0 # TODO: Implement
    p = 1
    for n in range(n_max):
        r, h = 0,0
        for i in range(len(reflists)):
            num_hyp_ngrams_in_refs_clipped, num_hyp_ngrams = get_ngram_counts(reflists[i], hyps[i], n+1)
            r += num_hyp_ngrams_in_refs_clipped
            h += num_hyp_ngrams
        p *= float(r/h)
    if p > 0:
        prec_mean = math.exp((1/n_max)*math.log(p))

    brevity_penalty, rl, hl = 0,0,0  # TODO: Implement
    for i in range(len(reflists)):
        ceiling = math.inf
        lr = 0
        for ref in reflists[i]:
            if ceiling > (abs(len(ref)-len(hyps[i]))):
                lr = len(ref)
        rl += lr
        hl += len(hyps[i])
    if float(hl/rl) <= 1:
        brevity_penalty = math.exp(1-1/float(hl/rl))
    else:
        brevity_penalty = 1

    # TODO: Implement
    bleu = brevity_penalty * prec_mean

    return bleu

def get_ngram_counts(refs, hyp, n):
    # ref_ngrams = [tuple(r[i:i + n]) for r in r for i in range(len(r) - n + 1)]
    ref_ngrams = []
    for r in refs:
        ref_ngrams.append([tuple(r[i:i + n]) for i in range(len(r) - n + 1)])
    hyp_ngrams = [tuple(hyp[i:i + n]) for i in range(len(hyp) - n + 1)]
    num_hyp_ngrams = max(1, len(hyp_ngrams))  # Avoid empty
    num_hyp_ngrams_in_refs_clipped = 0  # TODO: Implement
    count = Counter(hyp_ngrams)
    for i in list(set(hyp_ngrams)):
        ceiling = -9999
        for j in ref_ngrams:
            ceiling = max(ceiling, j.count(i))
        num_hyp_ngrams_in_refs_clipped += min(count[i], ceiling)
    return num_hyp_ngrams_in_refs_clipped, num_hyp_ngrams


