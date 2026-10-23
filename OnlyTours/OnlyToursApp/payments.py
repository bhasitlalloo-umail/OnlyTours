# Demo only: these card numbers are always declined (no real bank is used)
DECLINED_TEST_CARDS = {
    '4000000000000002': 'Your card was declined.',
    '4000000000009995': 'Your card has insufficient funds.',
}


def luhn_valid(number):
    """Luhn checksum: every real card number passes it, so it catches typos."""
    total = 0
    second = False  # True for every second digit, counting from the right
    for i in range(len(number) - 1, -1, -1):  # last digit first, down to the first
        value = int(number[i])
        if second:
            value = value * 2
            if value > 9:
                value = value - 9
        total = total + value
        second = not second
    return total % 10 == 0
