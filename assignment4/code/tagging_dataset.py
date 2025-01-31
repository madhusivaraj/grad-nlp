import os
import random
import statistics as stat
import torch

from torch.nn.utils.rnn import pad_sequence
from util import load_vertical_tagged_data


class TaggingDataset:

    def __init__(self, data_dir, batch_size, device, lower=True,
                 vocab_size=1000000000, pad='<pad>', unk='<unk>'):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.device = device
        self.lower = lower
        self.vocab_size = vocab_size
        self.PAD = pad
        self.UNK = unk
        self.PAD_ind = 0
        self.UNK_ind = 1
        self.populate_attributes()

    def populate_attributes(self):
        # Load training portion.
        (self.wordseqs_train, self.tagseqs_train, self.charseqslist_train,
         self.wordcounter_train, self.tagcounter_train, self.charcounter_train)\
         = load_vertical_tagged_data(os.path.join(self.data_dir, 'train.txt'))

        # Create index maps from training portion.
        self.word2x = self.get_imap(self.wordcounter_train,
                                    max_size=self.vocab_size, lower=self.lower)
        self.tag2y = self.get_imap(self.tagcounter_train, max_size=None,
                                   lower=False)
        self.char2c = self.get_imap(self.charcounter_train, max_size=None,
                                    lower=False)

        # Load validation and test portions.
        (self.wordseqs_val, self.tagseqs_val, self.charseqslist_val, _, _, _)\
            = load_vertical_tagged_data(os.path.join(self.data_dir, 'val.txt'))
        (self.wordseqs_test, self.tagseqs_test, self.charseqslist_test, _, _,
         _) = load_vertical_tagged_data(os.path.join(self.data_dir, 'test.txt'))

        # Prepare batches.
        self.batches_train = self.batchfy(self.wordseqs_train,
                                          self.tagseqs_train,
                                          self.charseqslist_train)
        self.batches_val = self.batchfy(self.wordseqs_val,
                                        self.tagseqs_val,
                                        self.charseqslist_val)
        self.batches_test = self.batchfy(self.wordseqs_test,
                                         self.tagseqs_test,
                                         self.charseqslist_test)

    def batchfy(self, wordseqs, tagseqs, charseqslist):
        batches = []

        def add_batch(xseqs, yseqs, cseqslist):
            if not xseqs:
                return
            X = torch.stack(xseqs).to(self.device)  # B x T
            Y = torch.stack(yseqs).to(self.device)  # B x T
            flattened_cseqs = [item for sublist in cseqslist for item in
                               sublist]  # List of BT tensors of varying lengths
            C = pad_sequence(flattened_cseqs, padding_value=self.PAD_ind,
                             batch_first=True).to(self.device)  # BT x T_char
            C_lens = torch.LongTensor([s.shape[0] for s in
                                       flattened_cseqs]).to(self.device)
            batches.append((X, Y, C, C_lens))

        xseqs = []
        yseqs = []
        cseqslist = []
        prev_length = float('inf')

        for i in range(len(wordseqs)):
            length = len(wordseqs[i])
            assert length <= prev_length  # Assume sequences in decr lengths

            wordseq = [word.lower() for word in wordseqs[i]] if self.lower \
                      else wordseqs[i]
            xseq = torch.LongTensor([self.word2x.get(word, self.UNK_ind)
                                    for word in wordseq])
            yseq = torch.LongTensor(
                [self.tag2y.get(tag, self.UNK_ind) for tag in tagseqs[i]])
            cseqs = [torch.LongTensor([self.char2c[c] for c in word
                                      if c in self.char2c])  # Skip unknown
                     for word in wordseqs[i]]  # Use original words

            if length < prev_length or len(xseqs) >= self.batch_size:
                add_batch(xseqs, yseqs, cseqslist)
                xseqs = []
                yseqs = []
                cseqslist = []

            xseqs.append(xseq)
            yseqs.append(yseq)
            cseqslist.append(cseqs)
            prev_length = length

        add_batch(xseqs, yseqs, cseqslist)

        return batches

    def log(self, logger):
        logger.log('-'*79)
        train_lengths = [len(xseq) for xseq in self.wordseqs_train]
        logger.log('Num train seqs:%d' % len(self.wordseqs_train))
        logger.log('\tAvg length:%d' % stat.mean(train_lengths))
        logger.log('\tMax length:%d' % max(train_lengths))
        logger.log('\tMin length:%d' % min(train_lengths))
        logger.log('\tStd length:%g' % stat.stdev(train_lengths))
        logger.log('Num val seqs:%d' % len(self.wordseqs_val))
        logger.log('Num test seqs:%d' % len(self.wordseqs_test))
        logger.log('')
        logger.log('Num word types:%d (including PAD/UNK)' %
                   len(self.word2x))
        logger.log('Num label types:%d (including PAD/UNK)' %
                   len(self.tag2y))
        logger.log('\t%s' % ' '.join(self.tag2y.keys()))
        logger.log('Num char types:%d (including PAD/UNK)' %
                   len(self.char2c))
        logger.log('\t%s' % ' '.join(self.char2c.keys()))

    def get_imap(self, counter, max_size=None, lower=False):
        imap = {self.PAD:self.PAD_ind, self.UNK:self.UNK_ind}
        if max_size is None or len(counter) <= max_size:
            strings = counter.keys()
        else:
            strings = list(zip(*sorted(counter.items(), key=lambda x:x[1],
                                       reverse=True)[:max_size]))[0]
        for string in strings:
            if lower:
                string = string.lower()
            if not string in imap:
                imap[string] = len(imap)
        return imap
