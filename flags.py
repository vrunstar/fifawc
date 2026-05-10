import os

NAME_MAP = {
    'mx': 'MEX', 'za': 'RSA', 'kr': 'KOR', 'cz': 'CZE',
    'br': 'BRA', 'ar': 'ARG', 'fr': 'FRA', 'de': 'GER',
    'es': 'ESP', 'gb-eng': 'ENG', 'pt': 'POR', 'nl': 'NED',
    'us': 'USA', 'ca': 'CAN', 'uy': 'URU', 'ec': 'ECU',
    'co': 'COL', 'ma': 'MAR', 'sn': 'SEN', 'eg': 'EGY',
    'ci': 'CIV', 'jp': 'JPN', 'ir': 'IRN', 'sa': 'KSA',
    'au': 'AUS', 'qa': 'QAT', 'uz': 'UZB', 'be': 'BEL',
    'hr': 'CRO', 'at': 'AUT', 'gb-sct': 'SCO', 'tr': 'TUR',
    'nz': 'NZL', 'pa': 'PAN', 'ba': 'BIH', 'ch': 'SUI',
    'ht': 'HAI', 'py': 'PAR', 'cw': 'CUW', 'se': 'SWE',
    'tn': 'TUN', 'cv': 'CPV', 'iq': 'IRQ', 'no': 'NOR',
    'dz': 'ALG', 'jo': 'JOR', 'cd': 'COD', 'gh': 'GHA',
}

for iso, code in NAME_MAP.items():
    old = f"static/flags/{iso}.png"
    new = f"static/flags/{code}.png"
    if os.path.exists(old):
        os.rename(old, new)
        print(f"✓ {iso}.png → {code}.png")