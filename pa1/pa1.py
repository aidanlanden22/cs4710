import sys

NOT_OPERATOR = '!'
AND_OPERATOR = '&'
OR_OPERATOR = '|'
precedence = {NOT_OPERATOR: 3, AND_OPERATOR: 2, OR_OPERATOR: 1,  '(': 0}

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
            v1 = operands.pop()
            v2 = operands.pop()
            operands.append(v1 and v2)
        elif token == '|':
            v1 = operands.pop()
            v2 = operands.pop()
            operands.append(v1 or v2)
        elif token == '!':
            v = operands.pop()
            operands.append(not v)
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


def query(postfix_expr):
    operands = []

    for token in postfix_expr:
        if token == '&':
            v1 = operands.pop()
            v2 = operands.pop()
            operands.append(v1 and v2)
        elif token == '|':
            v1 = operands.pop()
            v2 = operands.pop()
            operands.append(v1 or v2)
        elif token == '!':
            v = operands.pop()
            operands.append(not v)
        else:
            if token in facts:
                operands.append(True)
            else:
                truth = False
                for lhs, postfix, rhs in rules:
                    if rhs == token:
                        truth = truth or query(postfix)
                operands.append(truth)
    return operands[-1]


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


def is_operator(ch):
    return ch == AND_OPERATOR or ch == OR_OPERATOR or ch == NOT_OPERATOR or ch == '(' or ch == ')'


def tokenize(expr):
    i = 0
    tokens = []
    while i < len(expr):
        if is_operator(expr[i]):
            tokens.append(expr[i])
            i += 1
        else:
            j = i+1
            while j < len(expr) and not is_operator(expr[j]):
                j += 1
            tokens.append(expr[i:j])
            i = j
    return tokens


def imply(lhs, rhs):
    tokens = tokenize(lhs)
    postfix_expr = to_postfix(tokens)
    rules.append((lhs, postfix_expr, rhs))


def __main__():

    for line in sys.stdin:
        line = line.strip('\n\r ')
        s = line.split(' ')

        if s[0] == 'List':
            list_all()
        elif s[0] == 'Learn':
            learn()
        elif s[0] == 'Query':
            tokens = tokenize(s[1])
            postfix = to_postfix(tokens)
            if query(postfix):
                sys.stdout.write('true\n')
            else:
                sys.stdout.write('false\n')
        elif s[0] == 'Teach':
            if '=' in line:
                if '"' in line:
                    define(s[1], line[line.index('"'):])
                else:
                    assign(s[1], s[3])
            elif '->' in s:
                imply(s[1], s[3])


if __name__ == '__main__':
    __main__()
