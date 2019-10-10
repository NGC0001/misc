def calculate(s):
    priorDict = {
        '+':1, '-':1,
        '*':2, '/':2,
        '^':3,
    }
    opFunc = {
        '+':lambda a, b: a + b,
        '-':lambda a, b: a - b,
        '*':lambda a, b: a * b,
        '/':lambda a, b: a / b,
        '^':lambda a, b: a ** b,
    }
    ops = set(['+', '-', '*', '/', '^', '(', ')'])

    def get_expr(s, i):
        while i < len(s) and s[i] in (' ', '\t'):
            i += 1
        if i >= len(s):
            return None, i
        if s[i] in ops:
            return s[i], i+1
        j = i+1
        while j < len(s) and s[j] not in ops:
            j += 1
        v = float(s[i:j])
        return v, j

    def shrink_stack(prior=0):
        b = stk.pop()
        while len(stk) > 0 and stk[-1] != '(' and priorDict[stk[-1]] >= prior:
            op = stk.pop()
            a = stk.pop()
            b = opFunc[op](a, b)
        return b

    stk = []
    expr, i = get_expr(s, 0)
    while expr is not None:
        if expr in ops:
            if expr == '(':
                stk.append('(')
            elif expr == ')':
                b = shrink_stack()
                stk.pop()
                stk.append(b)
            elif expr in ('+', '-') and (len(stk) == 0 or stk[-1] == '('):
                stk.extend([0., expr])
            else:
                b = shrink_stack(priorDict[expr])
                stk.extend([b, expr])
        else:
            stk.append(expr)
        expr, i = get_expr(s, i)

    b = shrink_stack()
    return b
