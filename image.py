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
