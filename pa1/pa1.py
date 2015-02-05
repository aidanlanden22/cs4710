import sys

NOT_OPERATOR = '!'
AND_OPERATOR = '&'
OR_OPERATOR = '|'
precedence = {AND_OPERATOR: 1, OR_OPERATOR: 1, NOT_OPERATOR: 2, '(': 0}

variables = {}
facts = set([])
rules = []


def list_all():
    sys.stdout.write('Variables:\n')
    for name in sorted(variables):
        sys.stdout.write('\t%s = %s\n' % (name, variables[name]))

    sys.stdout.write('Facts:\n')
    for name in sorted(facts):
        sys.stdout.write('\t%s\n' % name)

    sys.stdout.write('Rules:\n')
    for lhs, _, rhs in rules:
        sys.stdout.write('\t%s -> %s\n' % (lhs, rhs))


def deduct(expr):
    operands = []
    for token in expr:
        if token == '&':
            v = operands.pop() and operands.pop()
            operands.append(v)
        elif token == '|':
            v = operands.pop() or operands.pop()
            operands.append(v)
        elif token == '!':
            v = not operands.pop()
            operands.append(v)
        else:
            if token in facts:
                operands.append(True)
            else:
                operands.append(False)
    return operands[-1]


def learn():
    while True:
        fixed = True
        for _, postfix, rhs in rules:
            if rhs in facts:
                continue
            if deduct(postfix):
                facts.add(rhs)
                fixed = False
        if fixed:
            break


def query(expr):
    pass


def define(name, value):
    variables[name] = value


def assign(name, value):
    if value.lower() == 'true':
        facts.add(name)
    elif value.lower() == 'false':
        if name in facts:
            facts.remove(name)


def to_postfix(expr):
    operators = []
    postfix = []
    for token in expr:
        if token == NOT_OPERATOR or token == AND_OPERATOR or token == OR_OPERATOR:
            while len(operators) > 0 and precedence[token] <= precedence[operators[-1]]:
                postfix.append(operators[-1])
                operators.pop()
            operators.append(token)
        elif token == '(':
            operators.append('(')
        elif token == ')':
            while operators[-1] != '(':
                postfix.append(operators.pop())
            operators.pop()
        else:
            postfix.append(token)
    while len(operators) > 0:
        postfix.append(operators.pop())
    return postfix


def imply(lhs, rhs):
    rules.append((lhs, to_postfix(lhs.split(' ')), rhs))


def __main__():
    for line in sys.stdin:
        line = line.strip('\n\r ')
        s = line.split(' ')

        if s[0] == 'List':
            list_all()
        elif s[0] == 'Learn':
            learn()
        elif s[0] == 'Query':
            query(s[1:])
        elif s[0] == 'Teach':
            if '=' in line:
                if '"' in line:
                    define(s[1], line[line.index('"'):])
                else:
                    assign(s[1], s[3])
            elif '->' in s:
                imply(line[line.index(' '):line.index('->')].strip(' '), s[-1])


if __name__ == '__main__':
    __main__()
