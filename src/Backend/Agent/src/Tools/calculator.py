"""
Stack-based expression calculator.

Evaluates infix arithmetic expressions using the shunting-yard algorithm:
1. Tokenize    (string -> tokens)
2. To Postfix  (infix tokens -> RPN via operator stack)
3. Eval Postfix(RPN -> result via operand stack)

Supports: +, -, *, /, //, %, **, parentheses, negative numbers, decimals.
"""

import operator


class CalculatorError(Exception):
    """Base exception for calculator errors."""
    pass


class TokenizeError(CalculatorError):
    pass


class EvalError(CalculatorError):
    pass


PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '//': 2, '%': 2, '**': 3}
LEFT_ASSOC = {'+', '-', '*', '/', '//', '%'}
RIGHT_ASSOC = {'**'}


def _tokenize(expr: str) -> list:
    """Convert expression string into a list of (type, value) tokens."""
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]

        if c.isspace():
            i += 1
            continue

        # number literal
        if c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                has_dot = has_dot or expr[j] == '.'
                j += 1
            raw = expr[i:j]
            tokens.append(('NUM', float(raw) if has_dot else int(raw)))
            i = j
            continue

        # parentheses
        if c in '()':
            tokens.append(('PAREN', c))
            i += 1
            continue

        # multi-char operators
        if c == '*' and i + 1 < len(expr) and expr[i + 1] == '*':
            tokens.append(('OP', '**'))
            i += 2
            continue
        if c == '/' and i + 1 < len(expr) and expr[i + 1] == '/':
            tokens.append(('OP', '//'))
            i += 2
            continue

        # single-char operators and unary handling
        if c in '+-*/%':
            if c == '-' and (not tokens or tokens[-1][0] == 'OP' or tokens[-1] == ('PAREN', '(')):
                # unary minus — try to parse as negative literal
                i += 1
                j = i
                has_dot = False
                while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                    has_dot = has_dot or expr[j] == '.'
                    j += 1
                if j > i:
                    raw = expr[i:j]
                    tokens.append(('NUM', -(float(raw) if has_dot else int(raw))))
                    i = j
                    continue
                # just a lonely '-' (rare but valid as unary op)
                tokens.append(('OP', '-'))
            elif c == '+' and (not tokens or tokens[-1][0] == 'OP' or tokens[-1] == ('PAREN', '(')):
                # unary plus — ignore
                i += 1
                continue
            else:
                tokens.append(('OP', c))
            i += 1
            continue

        raise TokenizeError(f"Unexpected character: {c!r}")

    return tokens


def _to_postfix(tokens: list) -> list:
    """Shunting-yard: infix tokens -> postfix (RPN) tokens."""
    output = []
    op_stack = []

    for typ, val in tokens:
        if typ == 'NUM':
            output.append(('NUM', val))
        elif typ == 'OP':
            while (
                op_stack
                and op_stack[-1] != '('
                and (
                    PRECEDENCE[op_stack[-1]] > PRECEDENCE[val]
                    or (PRECEDENCE[op_stack[-1]] == PRECEDENCE[val] and val in LEFT_ASSOC)
                )
            ):
                output.append(('OP', op_stack.pop()))
            op_stack.append(val)
        elif typ == 'PAREN':
            if val == '(':
                op_stack.append(val)
            else:
                while op_stack and op_stack[-1] != '(':
                    output.append(('OP', op_stack.pop()))
                if not op_stack:
                    raise EvalError("Mismatched parentheses")
                op_stack.pop()  # discard '('

    while op_stack:
        op = op_stack.pop()
        if op == '(':
            raise EvalError("Mismatched parentheses")
        output.append(('OP', op))

    return output


def _eval_postfix(postfix: list):
    """Evaluate RPN token list using an operand stack."""
    stack = []

    OPS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow,
    }

    for typ, val in postfix:
        if typ == 'NUM':
            stack.append(val)
        else:
            if len(stack) < 2:
                raise EvalError(f"Insufficient operands for {val!r}")
            b, a = stack.pop(), stack.pop()
            try:
                stack.append(OPS[val](a, b))
            except ZeroDivisionError:
                raise EvalError("Division by zero")
            except OverflowError:
                raise EvalError("Result overflow")

    if len(stack) != 1:
        raise EvalError("Invalid expression: leftover operands")
    return stack[0]


def main(expression: str):
    """Evaluate a mathematical expression and return the result.

    Args:
        expression: Infix arithmetic string, e.g. "3 + 4 * 2 / (1 - 5)".

    Returns:
        int if all operands were integers (no division that produces a float),
        otherwise float.

    Raises:
        CalculatorError: Invalid syntax, mismatched parens, division by zero, etc.
    """
    if not expression or not expression.strip():
        raise CalculatorError("Empty expression")

    tokens = _tokenize(expression)
    if not tokens:
        raise CalculatorError("Empty expression")
    postfix = _to_postfix(tokens)
    return _eval_postfix(postfix)


if __name__ == "__main__":
    tests = [
        ("1 + 2", 3),
        ("3 + 4 * 2", 11),
        ("(3 + 4) * 2", 14),
        ("10 / 3", 10 / 3),
        ("10 // 3", 3),
        ("2 ** 3", 8),
        ("2 ** 3 ** 2", 512),   # right-associative: 2^(3^2) = 512
        ("-5 + 3", -2),
        ("3.5 * 2", 7.0),
        ("(1 + 2 * (3 - 1))", 5),
        ("1 + -2", -1),
    ]

    for expr, expected in tests:
        try:
            result = main(expr)
            assert result == expected, f"{expr} => {result} != {expected}"
            print(f"  OK {expr:25s} = {result}")
        except Exception as e:
            print(f"  FAIL {expr:25s} raised {e}")

    # Edge cases
    try:
        main("")
    except CalculatorError:
        print(f"  OK {'(empty)':25s} raised CalculatorError")

    try:
        main("1 / 0")
    except CalculatorError:
        print(f"  OK {'1 / 0':25s} raised CalculatorError")

    try:
        main("(1 + 2")
    except CalculatorError:
        print(f"  OK {'(1 + 2':25s} raised CalculatorError")
