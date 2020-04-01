from collections import defaultdict

def inside(words,unary_rules,binary_rules):
    inside_prob=defaultdict(float)
    for i,word in enumerate(words,start=1):
        for urule in unary_rules.keys():
            if word==urule[1]:
                inside_prob[urule[0],i,i]=unary_rules[urule]

    for i in range(len(words)):
        for j in range(len(words)):
            for brule in binary_rules:
                rule0,rule1=brule[1].split()
                for k in range(j,i+j):
                    if inside_prob[rule0,j,k] and inside_prob[rule1,k+1,i+j]:
                        inside_prob[brule[0],j,i+j] += binary_rules[brule]*inside_prob[rule0,j,k]*inside_prob[rule1,k+1,i+j]
    return inside_prob


def outside(words,binary_rules,inside_prob):
    outside_prob=defaultdict(float)
    outside_prob['S',1,len(words)]=1

    for i in reversed(range(len(words))):
        for j in range(len(words) - i+1):
            for brule in binary_rules:
                rule0,rule1=brule[1].split()
                for k in range(i+j,len(words)+1):
                    outside_prob[rule0,j,i+j] += binary_rules[brule]*outside_prob[brule[0],j,k]*inside_prob[rule1,i+j+1,k]
            for rule in binary_rules:
                rule0,rule1=rule[1].split()
                for k in range(1,i+j):
                    outside_prob[rule1,j,i+j] += binary_rules[rule]*outside_prob[rule[0],k,i+j]*inside_prob[rule0,k,j-1]
    return outside_prob


if __name__=='__main__':
    words = 'the boy saw the man with a telescope'.split()

    unary_rules={('D','the'):4/6,
        ('D','a'):2/6,
        ('N','boy'):2/6,
        ('N','man'):2/6,
        ('N','telescope'):2/6,
        ('P','with'):1,
        ('V','saw'):1
    }
    binary_rules={
        ('S','NP VP'):1,
        ('NP','D N'):6/7,
        ('NP','NP PP'):1/7,
        ('VP','V NP'):2/3,
        ('VP','VP PP'):1/3,
        ('PP','P NP'):1
    }
    inside_probs=inside(words,unary_rules,binary_rules)
    outside_probs=outside(words,binary_rules,inside_probs)
    print(inside_probs['NP',4,8]*outside_probs['NP',4,8])
    print(inside_probs['VP',3,5]*outside_probs['VP',3,5])
