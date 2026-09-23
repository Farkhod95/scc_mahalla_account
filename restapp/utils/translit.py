"""
O'zbek kirill yozuvini lotinga o'girish (1995 yil alifbosi).

Loyihadagi mavjud ma'lumot bilan bir xil konvensiya:
`oʻ` va `gʻ` da MODIFIER LETTER TURNED COMMA (U+02BB) ishlatiladi —
`Bogʻishamol MFY`, `Oʻratepalik MFY` kabi.
"""

TURNED_COMMA = "ʻ"   # ʻ  — oʻ, gʻ uchun
APOSTROPHE = "ʼ"     # ʼ  — ъ uchun

# Ko'p harfli va maxsus belgilar birinchi tekshiriladi.
_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "j",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh",
    "ъ": APOSTROPHE, "ы": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ё": "yo", "ў": "o" + TURNED_COMMA, "қ": "q", "ғ": "g" + TURNED_COMMA,
    "ҳ": "h",
    # Ba'zi fayllarda lotin ' bilan yozilgan kirill harflari uchrайdi
    "ө": "o" + TURNED_COMMA, "ү": "u", "ң": "ng",
}

VOWELS_CYR = set("аеёиоуўэюяы")


def _apply_case(latin: str, upper: bool, next_upper: bool) -> str:
    """Ko'p harfli natijaga manba harf registrini qo'llaydi."""
    if not upper or not latin:
        return latin
    if len(latin) == 1:
        return latin.upper()
    # СОАТОВ -> SOATOV (keyingi harf ham bosh harf) ; Соатов -> Soatov
    return latin.upper() if next_upper else latin[0].upper() + latin[1:]


def to_latin(text) -> str:
    """
    Kirill matnni lotinga o'giradi. Lotin harflar, raqamlar va tinish
    belgilari o'zgarishsiz qoladi.

    `е` so'z boshida `ye` bo'ladi (Ерматов -> Yermatov), aks holda `e`.
    """
    if text is None:
        return ""
    text = str(text)
    out = []

    for i, ch in enumerate(text):
        lower = ch.lower()
        if lower not in _MAP:
            out.append(ch)
            continue

        upper = ch.isupper()
        # keyingi harf bosh harfmi (ALL CAPS ni aniqlash uchun)
        nxt = text[i + 1] if i + 1 < len(text) else ""
        next_upper = nxt.isupper() or not nxt.isalpha()

        latin = _MAP[lower]

        # `е`: so'z boshida yoki unlidan keyin -> ye
        if lower == "е":
            prev = text[i - 1] if i else ""
            if not prev.isalpha() or prev.lower() in VOWELS_CYR:
                latin = "ye"

        out.append(_apply_case(latin, upper, next_upper))

    return "".join(out)


def to_latin_name(text) -> str:
    """
    Ism-familiya uchun: lotinga o'giradi va HAR BIR SO'ZNI bosh harf bilan
    yozadi (fayllarda ismlar ko'pincha BOSH HARFLAR bilan: `СОАТОВ ДАВРОН`).

    `oʻ`/`gʻ` ichidagi ʻ so'z bo'luvchi deb qaralmaydi.
    """
    latin = to_latin(text)
    if not latin:
        return ""

    words = []
    for word in latin.split():
        if not word:
            continue
        # ALL CAPS yoki hammasi kichik bo'lsa — birinchi harfni bosh qilamiz.
        if word.isupper() or word.islower():
            words.append(word[0].upper() + word[1:].lower())
        else:
            words.append(word)
    return " ".join(words)
