import itertools
import torch
import torch.nn as nn


class CRFLoss(nn.Module):

    def __init__(self, L, init): # L = number of label types
        super(CRFLoss, self).__init__()
        self.start = nn.Parameter(torch.Tensor(L).uniform_(-init, init))
        self.T = nn.Parameter(torch.Tensor(L, L).uniform_(-init, init))
        self.end = nn.Parameter(torch.Tensor(L).uniform_(-init, init))

    def forward(self, scores, targets):
        #   scores  (B x T x L), assumes no padding
        #   targets (B x T), assumes no padding
        normalizers = self.compute_normalizers(scores)
        target_scores = self.score_targets(scores, targets)
        loss = (normalizers - target_scores).mean()
        return loss

    def decode(self, scores): # B x T x L
        B, T, L = scores.size()
        prev = self.start + scores[:,0,:]  # TODO (B x L)
        back = []
        for i in range(1, T):
            prev, indices = (prev.unsqueeze(2) + torch.t(self.T) + scores[:,i,:].unsqueeze(1)).max(dim=1)
            back.append(indices)
        max_scores, indices = (prev+self.end).max(dim=1)  # TODO (indices:B)
        tape = [indices]
        for i in range(T - 1):
            indices = torch.gather(back[-i-1], 1, indices.unsqueeze(-1)).squeeze(-1)  # TODO
            tape.append(indices)
        return max_scores, torch.stack(tape[::-1], dim=1)

    def decode_brute(self, scores):
        B, T, L = scores.size()
        all_targets = []
        yseq_scores = []
        for yseq in itertools.product(list(range(L)), repeat=T):
            targets = torch.LongTensor(yseq).expand(B, T)
            all_targets.append(torch.LongTensor(yseq))
            yseq_scores.append(self.score_targets(scores, targets))
        max_scores, indices = torch.stack(yseq_scores).max(dim=0)

        return max_scores, torch.stack(all_targets)[indices]

    def compute_normalizers(self, scores):
        B, T, L = scores.size()
        prev = self.start.expand(B,L) + scores[:,0,:] # TODO (B x L)
        for i in range(1, T):
            prev = torch.logsumexp(prev.unsqueeze(2) + scores[:, i, :].unsqueeze(1) + self.T.transpose(0, 1), dim=1) # TODO:implement only using prev (no new definition)
        normalizers = (prev + self.end.expand(B, L)).logsumexp(dim=1) # TODO (B)
        return normalizers

    def compute_normalizers_brute(self, scores):
        B, T, L = scores.size()
        yseq_scores = []
        for yseq in itertools.product(list(range(L)), repeat=T):
            targets = torch.LongTensor(yseq).expand(B, T)
            yseq_scores.append(self.score_targets(scores, targets))
        normalizers = torch.stack(yseq_scores).logsumexp(dim=0)
        return normalizers

    def score_targets(self, scores, targets):
        B, T, L = scores.size()
        emits = scores.gather(2, targets.unsqueeze(2)).squeeze(2).sum(1)  # B
        trans = torch.stack(
            [self.start.gather(0, targets[:, 0])] +
            [self.T[targets[:, i], targets[:, i - 1]] for i in range(1, T)] +
            [self.end.gather(0, targets[:, -1])]).sum(0)  # B
        return emits+trans  # B


class GreedyLoss(nn.Module):

    def __init__(self):
        super(GreedyLoss, self).__init__()
        self.avgCE = nn.CrossEntropyLoss(reduction='mean')

    def forward(self, scores, targets):
        #   scores  (B x T x L), assumes no padding
        #   targets (B x T), assumes no padding
        B, T, L = scores.size()
        scores = scores.view(-1, L)   # BT x L
        targets = targets.view(B*T) # BT
        loss = self.avgCE(scores, targets)
        return loss

    def decode(self, scores): # B x T x L
        _, indices = scores.max(2)
        return None, indices  # B x T
