import re

# Emoji ranges, plus the joiner, variation selector and keycap characters that combine emojis
EMOJI_PATTERN = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u231A\u231B\u23E9-\u23FA"
    "\U000E0020-\U000E007F\u200D\uFE0F\u20E3]"
)


# One or more emojis in a row, with the spaces and line breaks around them
EMOJI_RUN_PATTERN = re.compile(r"\s*(?:" + EMOJI_PATTERN.pattern + r"+\s*)+")


def removeEmojis(text):
    # Keycap emojis like 1️⃣ become the plain digit
    text = re.sub("([0-9#*])\uFE0F?\u20E3", r"\1", text)
    # Replace emojis with a comma, so the TTS makes a short pause instead of reading them
    text = EMOJI_RUN_PATTERN.sub(", ", text)
    # No comma right after another punctuation mark, and none at the start or end
    text = re.sub(r"([.,!?;:…])\s*,\s*", r"\1 ", text)
    text = text.strip(" ,")
    return re.sub(r"[ \t]{2,}", " ", text)
