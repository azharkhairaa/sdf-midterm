'''Software Development Fundamentals (SDF05) midterm, code answers for C1 and D1.

Muhammad Azhar Khaira (25120300010)

    python3 answers.py              # runs the demonstrations and every test below
    python3 -m pytest answers.py    # same tests through pytest (optional)
'''
import itertools
import math

# C1: legacy function, copied as-is from the exam

def p(x, y, f):
    t = x * y
    if f:
        t = t * 0.9
    return t * 1.11

# C1 b: refactored version

# factors keep the exact float literals of the legacy code so results stay bit-identical
MEMBER_DISCOUNT_FACTOR = 0.9  # members pay 90% of the subtotal (10% discount)
TAX_FACTOR = 1.11  # 11% VAT added on top of the discounted amount

def calculate_subtotal(unit_price: float, quantity: int) -> float:
    return unit_price * quantity

def apply_member_discount(amount: float, is_member: bool) -> float:
    if is_member:
        return amount * MEMBER_DISCOUNT_FACTOR
    return amount

def apply_tax(amount: float) -> float:
    return amount * TAX_FACTOR

def calculate_order_total(unit_price: float, quantity: int, is_member: bool) -> float:
    '''Total price after the member discount (if any) and tax.'''
    subtotal = calculate_subtotal(unit_price, quantity)
    discounted = apply_member_discount(subtotal, is_member)
    return apply_tax(discounted)

# C1 c: same result as p(), bit for bit

def test_refactor_matches_legacy_exactly():
    unit_prices = [0, 1, 3500, 25000, 99999.99, 0.1]
    quantities = [0, 1, 3, 12]
    for unit_price, quantity, is_member in itertools.product(unit_prices, quantities, [True, False]):
        assert calculate_order_total(unit_price, quantity, is_member) == p(unit_price, quantity, is_member)

# C1 d: test to add

def test_non_member_pays_subtotal_plus_tax():
    assert math.isclose(calculate_order_total(50_000, 3, False), 166_500)

# D1: version before the pull request

def calculate_average_before(scores):
    return sum(scores) / len(scores)

# D1: version proposed by the pull request, unchanged

def calculate_average_pr(scores):
    d = scores
    total = 0
    for i in range(len(d)):
        total = total + d[i]
    return total / len(d) + 1

# D1 e: version recommended in the review

def calculate_average(scores):
    '''Arithmetic mean of scores, raises ValueError for an empty list.'''
    if not scores:
        raise ValueError('scores must not be empty')
    return sum(scores) / len(scores)

# D1 d: test requested from the author

def test_average_of_2_4_6_is_4():
    assert calculate_average([2, 4, 6]) == 4

# D1 e: empty list is rejected with a clear error

def test_empty_list_raises_value_error():
    try:
        calculate_average([])
    except ValueError as error:
        assert str(error) == 'scores must not be empty'
    else:
        raise AssertionError('expected ValueError')

def describe_call(function, scores):
    try:
        return repr(function(scores))
    except Exception as error:
        return f"{type(error).__name__}: {error}"

def main():
    print('C1 c: x=100000, y=2, f=True')
    print('  legacy p     :', repr(p(100_000, 2, True)))
    print('  refactored   :', repr(calculate_order_total(100_000, 2, True)))
    print()
    print('D1 c: scores = [2, 4, 6]')
    print('  before PR    :', describe_call(calculate_average_before, [2, 4, 6]))
    print('  after PR     :', describe_call(calculate_average_pr, [2, 4, 6]))
    print()
    print('D1 e: scores = []')
    print('  before PR    :', describe_call(calculate_average_before, []))
    print('  after PR     :', describe_call(calculate_average_pr, []))
    print('  recommended  :', describe_call(calculate_average, []))
    print()
    print('D1 d: requested test against the PR version')
    print('  [2, 4, 6] == 4 :', calculate_average_pr([2, 4, 6]) == 4, '(the test catches the + 1)')
    print()
    tests = [value for name, value in globals().items() if name.startswith('test_')]
    for test in tests:
        test()
        print('PASS', test.__name__)

if __name__ == '__main__':
    main()