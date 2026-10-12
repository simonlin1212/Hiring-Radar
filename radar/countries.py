"""两位国家码 ↔ 英文国名（常见国家）。用于把来源给的国名统一成国家码。"""
NAMES = {
    "US": "United States", "GB": "United Kingdom", "CA": "Canada", "AU": "Australia", "NZ": "New Zealand",
    "IE": "Ireland", "DE": "Germany", "FR": "France", "NL": "Netherlands", "BE": "Belgium", "LU": "Luxembourg",
    "CH": "Switzerland", "AT": "Austria", "ES": "Spain", "PT": "Portugal", "IT": "Italy", "SE": "Sweden",
    "NO": "Norway", "DK": "Denmark", "FI": "Finland", "IS": "Iceland", "PL": "Poland", "CZ": "Czechia",
    "SK": "Slovakia", "HU": "Hungary", "RO": "Romania", "BG": "Bulgaria", "GR": "Greece", "HR": "Croatia",
    "SI": "Slovenia", "RS": "Serbia", "EE": "Estonia", "LV": "Latvia", "LT": "Lithuania", "UA": "Ukraine",
    "TR": "Turkey", "CY": "Cyprus", "MT": "Malta", "IL": "Israel", "AE": "United Arab Emirates",
    "SA": "Saudi Arabia", "QA": "Qatar", "EG": "Egypt", "ZA": "South Africa", "NG": "Nigeria", "KE": "Kenya",
    "MA": "Morocco", "IN": "India", "PK": "Pakistan", "BD": "Bangladesh", "LK": "Sri Lanka", "SG": "Singapore",
    "MY": "Malaysia", "ID": "Indonesia", "PH": "Philippines", "TH": "Thailand", "VN": "Vietnam", "HK": "Hong Kong",
    "TW": "Taiwan", "CN": "China", "JP": "Japan", "KR": "South Korea", "MX": "Mexico", "BR": "Brazil",
    "AR": "Argentina", "CL": "Chile", "CO": "Colombia", "PE": "Peru", "UY": "Uruguay", "CR": "Costa Rica",
}
_ALIAS = {"usa": "US", "united states of america": "US", "uk": "GB", "england": "GB", "scotland": "GB",
          "wales": "GB", "great britain": "GB", "czech republic": "CZ", "korea": "KR", "republic of korea": "KR",
          "uae": "AE", "türkiye": "TR", "viet nam": "VN", "aotearoa": "NZ"}
_BY_NAME = {v.lower(): k for k, v in NAMES.items()}
_BY_NAME.update(_ALIAS)


def code(name):
    """国名或国家码 → 两位码；认不出返回空串。"""
    s = (name or "").strip()
    if len(s) == 2 and s.upper() in NAMES:
        return s.upper()
    return _BY_NAME.get(s.lower(), "")


def name(cc):
    return NAMES.get((cc or "").upper(), cc or "")
