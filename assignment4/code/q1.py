def forward(words):
    forward_prob=[{}]
    for tag in tags:
        forward_prob[0][tag]=transition_prob['*'][tag]*emission_prob[tag][words[0]]
    for i, obs in enumerate(words[1:],1):
        forward_prob.append({})
        for tag in tags:
            prob=0
            for prev in tags:
                prob+=forward_prob[i-1][prev]*transition_prob[prev][tag]*emission_prob[tag][obs]
            forward_prob[i][tag]=prob
    return forward_prob

def backward(words):
    backward_prob=[{} for i in range(len(words))]
    for tag in tags:
        backward_prob[-1][tag]=transition_prob[tag]['STOP']
    for i, obs in reversed(list(enumerate(words[:-1]))):
        for tag in tags:
            prob=0
            for prev in tags:
                prob+=forward_prob[i+1][prev]*transition_prob[tag][prev]*emission_prob[prev][words[i + 1]]
            backward_prob[i][tag]=prob
    return backward_prob

if __name__=='__main__':
    states = ['the', 'saw', 'cut', 'man']
    tags = ['D', 'N', 'V']
    transition_prob = {'*':{'D':2/3, 'N':1/3, 'V':0, 'STOP':0},
                        'D':{'D':0, 'N':1, 'V':0, 'STOP':0},
                        'N':{'D':0, 'N':1/6, 'V':2/6, 'STOP':3/6},
                        'V':{'D':1, 'N':0, 'V':0, 'STOP':0}}
    emission_prob = {'D':{'the':1, 'man':0, 'saw':0, 'cut':0},
                       'N':{'the':1/6, 'man':2/6, 'saw':2/6, 'cut':1/6},
                       'V':{'the':0, 'man':0, 'saw':1/2, 'cut':1/2}}
    sentences = ['the saw cut the man', 'the man saw the cut']

    for sentence in sentences:
        if not type(sentence) == type(list):
            words=sentence.split(' ')
        forward_prob=forward(words)
        backward_prob=backward(words)
        mu = [{} for i in range(len(forward_prob))]
        for i in range(len(forward_prob)):
            fp=forward_prob[i]
            bp=backward_prob[i]
            for tag in bp:
                mu[i][tag]=fp[tag]*bp[tag]
        if sentence == sentence[0]:
            print(mu[2]['V'])
        else:
            print(mu[4]['N'])