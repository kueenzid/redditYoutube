import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import random

def add_awards(draw, image, awards_x, awards_y):
    award_size = 60
    award_spacing = 10
    font_size = 30

    # Load award icons
    awards_folder = os.path.join("assets", "awards")
    awards = [os.path.join(awards_folder, f) for f in os.listdir(awards_folder) if os.path.isfile(os.path.join(awards_folder, f))]
    selected_awards = random.sample(awards, 4)
    award_y = awards_y + award_spacing

    # Add awards to the image in one line
    for i, award_path in enumerate(selected_awards):
        award_icon = Image.open(award_path).resize((award_size, award_size))
        award_x = awards_x + award_spacing + i * (award_spacing + award_size + font_size)
        image.paste(award_icon, (award_x, award_y), award_icon.convert('RGBA'))
        award_count = random.randint(1, 30)
        draw.text((award_x + award_size + award_spacing, award_y + ((award_size + award_spacing) / 2 - font_size/2)), str(award_count), fill="grey", font=ImageFont.load_default(), size=font_size)


def create_custom_image(output_path, text):
    # Define image dimensions
    width = 1280  # 720p width
    height = 720  # Initial height, will adjust later if needed
    padding = 50

    # Create a blank image with white background
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load the profile icon
    icon_path = os.path.join("assets", "profileIcon.webp")
    icon = Image.open(icon_path)
    icon = icon.resize((100, 100))
    icon_x = padding
    icon_y = padding
    image.paste(icon, (icon_x, icon_y), icon.convert('RGBA'))
    
    draw.text((icon_x + 110, icon_y + 35), "r/name", fill="black", font=ImageFont.load_default())

    # Awards section
    awards_x = width - 400
    awards_y = padding
    add_awards(draw, image, awards_x, awards_y)

    # Text section
    text_x = 50
    text_y = 200
    draw.text((text_x, text_y), text, fill="black", font=ImageFont.load_default())

    # Save the image
    image.save(output_path)


def load_font(size):
    # The default Pillow font has no umlauts, so prefer a system font
    for name in ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def wrap_text(text, font, max_width):
    lines = []
    for word in text.split():
        if lines and ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(f"{lines[-1]} {word}", font=font) <= max_width:
            lines[-1] = f"{lines[-1]} {word}"
        else:
            lines.append(word)
    return lines


def create_title_card(output_path, title, subtitle, highlight=None):
    width = 1000
    padding = 50
    title_font = load_font(56)
    subtitle_font = load_font(32)
    highlight_font = load_font(72)

    lines = wrap_text(title, title_font, width - 2 * padding)

    line_height = 70
    highlight_height = 110 if highlight else 0
    height = 2 * padding + 60 + len(lines) * line_height + highlight_height

    image = Image.new("RGB", (width, height), "#1a1a1b")
    draw = ImageDraw.Draw(image)
    draw.text((padding, padding), subtitle, fill="grey", font=subtitle_font)
    for i, line in enumerate(lines):
        draw.text((padding, padding + 60 + i * line_height), line, fill="white", font=title_font)
    if highlight:
        draw.text((padding, padding + 60 + len(lines) * line_height + 30), highlight, fill="#FFD400", font=highlight_font)

    image.save(output_path)


# 20min reactions in the order and colours of 20min.ch: (label, API key, background, text colour)
reaction_styles = [
    ("Genau", "exact", "#2659FF", "white"),
    ("Love it", "awesome", "#DB009F", "white"),
    ("Smart", "smart", "#008666", "white"),
    ("Unnötig", "unnecessary", "#B585EB", "#07184C"),
    ("Quatsch", "nonsense", "#7332FF", "white"),
    ("So nicht", "bad", "#07184C", "white"),
]


def create_comment_card(output_path, author, reactions):
    width = 1000
    padding = 35
    avatar_size = 100
    name_font = load_font(44)
    pill_font = load_font(28)
    pill_height = 56
    pill_gap = 12
    bar_height = 14

    # Lay out the reaction pills, wrapping into a new row when the card is full
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pills = []
    x, y = padding, padding + avatar_size + 25
    for label, key, background, color in reaction_styles:
        text = f"{label.upper()} {reactions.get(key, 0)}"
        pill_width = measure.textlength(text, font=pill_font) + 2 * 20
        if x + pill_width > width - padding:
            x, y = padding, y + pill_height + pill_gap
        pills.append((x, y, pill_width, text, background, color))
        x += pill_width + pill_gap
    bar_y = y + pill_height + 20
    height = bar_y + bar_height + padding

    image = Image.new("RGB", (width, height), "#1a1a1b")
    draw = ImageDraw.Draw(image)

    # Avatar with the first letter of the (censored) nickname
    avatar_box = (padding, padding, padding + avatar_size, padding + avatar_size)
    draw.ellipse(avatar_box, fill="#0D2880")
    draw.text(((avatar_box[0] + avatar_box[2]) / 2, (avatar_box[1] + avatar_box[3]) / 2), author[:1].upper(), fill="white", font=name_font, anchor="mm")
    draw.text((padding + avatar_size + 30, padding + avatar_size / 2), author, fill="white", font=name_font, anchor="lm")

    for x, y, pill_width, text, background, color in pills:
        draw.rounded_rectangle((x, y, x + pill_width, y + pill_height), radius=10, fill=background)
        draw.text((x + pill_width / 2, y + pill_height / 2), text, fill=color, font=pill_font, anchor="mm")

    # Bar with the share of each reaction
    total = sum(reactions.get(key, 0) for _, key, _, _ in reaction_styles)
    if total:
        bar_x = padding
        bar_width = width - 2 * padding
        for _, key, background, _ in reaction_styles:
            share = reactions.get(key, 0) / total * bar_width
            # Leave a gap of 6 px between the segments
            segment_width = share - 6
            if segment_width >= 1:
                draw.rounded_rectangle((bar_x, bar_y, bar_x + segment_width, bar_y + bar_height), radius=min(bar_height, segment_width) / 2, fill=background)
            bar_x += share

    image.save(output_path)
