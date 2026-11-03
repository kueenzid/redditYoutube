import re

# Emoji ranges, plus the joiner, variation selector and keycap characters that combine emojis
EMOJI_PATTERN = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u231A\u231B\u23E9-\u23FA"
    "\U000E0020-\U000E007F\u200D\uFE0F\u20E3]"
)


def removeEmojis(text):
    # Remove emojis so the TTS does not read them, then fix the spaces they leave
    text = EMOJI_PATTERN.sub("", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()
