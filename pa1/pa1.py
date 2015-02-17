import sys
import collections

NOT_OPERATOR = '!'
AND_OPERATOR = '&'
OR_OPERATOR = '|'
precedence = {NOT_OPERATOR: 3, AND_OPERATOR: 2, OR_OPERATOR: 1,  '(': 0}

variables = collections.OrderedDict()
facts = collections.OrderedDict()
rules = []


def is_operator(ch):
    return ch == AND_OPERATOR or ch == OR_OPERATOR or ch == NOT_OPERATOR or ch == '(' or ch == ')'


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


def define_var(name, value):
    variables[name] = value.strip('"')


def assign_var(name, value):
    if value.lower() == 'true':
        facts[name] = True
    elif value.lower() == 'false':
        if name in facts:
            facts.pop(name)


def set_rule(lhs, rhs):
    tokens = tokenize(lhs)
    postfix_expr = to_postfix(tokens)
    rules.append((lhs, postfix_expr, rhs))


def list_all():
    sys.stdout.write('Variables:\n')
    for name in variables:
        sys.stdout.write('\t%s = %s\n' % (name, variables[name]))

    sys.stdout.write('Facts:\n')
    for name in facts:
        sys.stdout.write('\t%s\n' % name)

    sys.stdout.write('Rules:\n')
    for lhs, _, rhs in rules:
        sys.stdout.write('\t%s -> %s\n' % (lhs, rhs))


def learn():
    while True:
        fixed = True
        for _, postfix, rhs in rules:
            if rhs in facts:
                continue
            if deduct(postfix):
                facts[rhs] = True
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


def why(postfix_expr):
    operands = []
    reasoning = []

    for token in postfix_expr:
        if token == '&':
            v1, e1 = operands.pop()
            v2, e2 = operands.pop()

            operands.append((v1 and v2, '(%s AND %s)' % (e2, e1)))
            if v1 and v2:
                reasoning.append('I THUS KNOW THAT %s AND %s' % (e2, e1))
            else:
                reasoning.append('THUS I CANNOT PROVE %s AND %s' % (e2, e1))
        elif token == '|':
            v1, e1 = operands.pop()
            v2, e2 = operands.pop()
            operands.append((v1 or v2, '(%s OR %s)' % (e2, e1)))
            if v1 or v2:
                reasoning.append('I THUS KNOW THAT %s OR %s' % (e2, e1))
            else:
                reasoning.append('THUS I CANNOT PROVE %s OR %s' % (e2, e1))
        elif token == '!':
            v, e = operands.pop()
            operands.append((not v, '(NOT %s)' % e))
            if not v:
                reasoning.append('I THUS KNOW THAT NOT %s' % e)
            else:
                reasoning.append('THUS I CANNOT PROVE NOT %s' % e)
        else:
            has_rule = False
            truth = False

            var_reasoning = []
            var_rules = []

            for lhs, postfix, rhs in rules:
                if rhs == token:
                    has_rule = True
                    expr_truth, expr_rule, expr_reasoning = why(postfix)
                    var_reasoning = var_reasoning + expr_reasoning
                    var_rules.append(expr_rule)
                    truth = truth or expr_truth
                    if truth:
                        var_reasoning = expr_reasoning
                        var_rules = [expr_rule]
                        break

            reasoning = reasoning + var_reasoning
            if has_rule:
                operands.append((truth, variables[token]))
                if truth:
                    reasoning.append('BECAUSE %s I KNOW THAT %s' % (var_rules[0], variables[token]))
                else:
                    for var_rule in var_rules:
                        reasoning.append('BECAUSE IT IS NOT TRUE THAT %s I CANNOT PROVE'
                                         ' %s' % (var_rule, variables[token]))

            else:
                operands.append((token in facts, variables[token]))
                if token in facts:
                    reasoning.append("I KNOW THAT %s" % variables[token])
                else:
                    reasoning.append("I KNOW IT IS NOT TRUE THAT %s" % variables[token])

    #print(operands[-1][0], operands[-1][1], reasoning)
    return operands[-1][0], operands[-1][1], reasoning


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
        elif s[0] == 'Why':
            tokens = tokenize(s[1])
            postfix = to_postfix(tokens)
            truth, rule, reasoning = why(postfix)
            if truth:
                sys.stdout.write('true\n')
            else:
                sys.stdout.write('false\n')
            for reason in reasoning:
                sys.stdout.write(reason + '\n')
        elif s[0] == 'Teach':
            if '=' in line:
                if '"' in line:
                    define_var(s[1], line[line.index('"'):])
                else:
                    assign_var(s[1], s[3])
            elif '->' in s:
                set_rule(s[1], s[3])


if __name__ == '__main__':
    __main__()
