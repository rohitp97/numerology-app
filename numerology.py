"""Numerology calculation engine — Chaldean system (Arun Pandit)."""

from datetime import date

# Chaldean letter values (9 is sacred, not assigned)
CHALDEAN_VALUES = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8,
}

VOWELS = set('AEIOU')

# Lo Shu Grid layout (top to bottom): 4,9,2 / 3,5,7 / 8,1,6
LOSHU_ROWS = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]


def reduce_number(n, keep_master=True):
    """Reduce to single digit, optionally preserving master numbers 11, 22, 33."""
    while n > 9:
        if keep_master and n in (11, 22, 33):
            break
        n = sum(int(d) for d in str(n))
    return n


def get_mulank(day: int) -> int:
    return reduce_number(day)


def get_bhagyank(day: int, month: int, year: int) -> int:
    total = sum(int(d) for d in f"{day:02d}{month:02d}{year:04d}")
    return reduce_number(total)


def get_personal_year(day: int, month: int, current_year: int = None) -> int:
    if current_year is None:
        current_year = date.today().year
    total = sum(int(d) for d in f"{day:02d}{month:02d}{current_year:04d}")
    return reduce_number(total, keep_master=False)  # Personal Year always reduces to single digit


def get_personality(name: str) -> int:
    """Personality Number — Chaldean values of CONSONANTS."""
    total = sum(
        CHALDEAN_VALUES.get(c.upper(), 0) for c in name.upper()
        if c.isalpha() and c not in VOWELS
    )
    return reduce_number(total)


def get_soul_urge(name: str) -> int:
    """Soul Urge — Chaldean values of VOWELS."""
    total = sum(CHALDEAN_VALUES.get(c.upper(), 0) for c in name.upper() if c in VOWELS)
    return reduce_number(total)


def get_success_number(day: int, month: int) -> int:
    """Success Number = Day + Month, reduced."""
    return reduce_number(day + month)


def get_connection_number(mulank: int, bhagyank: int) -> int:
    """Connection Number = Mulank + Bhagyank, reduced."""
    return reduce_number(mulank + bhagyank)


def get_name_number(name: str) -> int:
    """Full Name Number — Chaldean values of ALL letters, reduced."""
    total = sum(CHALDEAN_VALUES.get(c.upper(), 0) for c in name.upper() if c.isalpha())
    return reduce_number(total)


def get_maturity_number(bhagyank: int, name_number: int) -> int:
    """Maturity Number = Bhagyank + Full Name Number, reduced."""
    return reduce_number(bhagyank + name_number)


def get_loshu_grid(day: int, month: int, year: int) -> dict:
    dob_str = f"{day:02d}{month:02d}{year:04d}"
    counts = {i: 0 for i in range(1, 10)}
    for ch in dob_str:
        d = int(ch)
        if 1 <= d <= 9:
            counts[d] += 1
    # Include Bhagyank in the grid — always reduce to single digit (master numbers like 33 → 6)
    bhagyank = get_bhagyank(day, month, year)
    bhagyank_digit = reduce_number(bhagyank, keep_master=False)
    if 1 <= bhagyank_digit <= 9:
        counts[bhagyank_digit] += 1
    return counts


def get_missing_numbers(grid: dict) -> list:
    return [n for n in range(1, 10) if grid[n] == 0]


def calculate_all(name: str, day: int, month: int, year: int) -> dict:
    mulank = get_mulank(day)
    bhagyank = get_bhagyank(day, month, year)
    personality = get_personality(name)
    soul_urge = get_soul_urge(name)
    name_number = get_name_number(name)
    success = get_success_number(day, month)
    connection = get_connection_number(mulank, bhagyank)
    maturity = get_maturity_number(bhagyank, name_number)
    personal_year = get_personal_year(day, month)
    grid = get_loshu_grid(day, month, year)
    missing = get_missing_numbers(grid)
    first_letter = name.strip()[0].upper() if name.strip() else ''

    return {
        'name': name,
        'dob': f"{day:02d}/{month:02d}/{year:04d}",
        'mulank': mulank,
        'bhagyank': bhagyank,
        'personality': personality,
        'soul_urge': soul_urge,
        'name_number': name_number,
        'success': success,
        'connection': connection,
        'maturity': maturity,
        'personal_year': personal_year,
        'current_year': date.today().year,
        'grid': grid,
        'missing': missing,
        'first_letter': first_letter,
        'loshu_rows': LOSHU_ROWS,
    }
