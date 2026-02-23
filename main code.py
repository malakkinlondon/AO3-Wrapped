# %%
# Code Cell #1 (Configuration)

# Path to your exported bookmarks CSV file
BOOKMARK_CSV_PATH = "/content/Stats.csv"

# Please change to the current year as needed.
wrapped_year = 2026

# OPTIONAL - fic titles to exclude (example format: ["Title 1", "Title 2"])
fics_to_exclude = []

# OPTIONAL - same but for authors
authors_to_exclude = []

# %%

# Code Cell #2 (Library Fetching)
# Installing other libraries and fetching blank pictures to fill
!git clone https://github.com/malakkinlondon/AO3_Wrapped_blank_images.git AO3_wrapped_blank_images
!pip install unidecode

# %%

# Code Cell #3
import csv
from datetime import datetime

from PIL import Image
import numpy as np
from collections import Counter
import IPython.display as Idisplay
import io
from PIL import ImageDraw, ImageFont
import string
from unidecode import unidecode

class Fic:
  def __init__(self, link, title, rating, authors, fandoms, language, relationships, characters, freeforms, words):
    self.link = link
    self.title = title
    self.rating = rating
    self.authors = authors
    self.fandoms = fandoms
    self.relationships = relationships
    self.characters = characters
    self.freeforms = freeforms
    self.language = language
    self.words = words

  def __eq__(self, other):
    return isinstance(other, Fic) and self.link == other.link

  def __hash__(self):
     return hash(self.link)

def load_bookmarks_csv(path):
# Load tab-separated AO3 bookmarks CSV.
  with open(path, newline="", encoding="utf-8") as f:
    sample = f.read(4096)
    f.seek(0)

    if ";" in sample and sample.count(";") > sample.count(","):
        delimiter = ";"
    elif "\t" in sample:
        delimiter = "\t"
    else:
        delimiter = ","
    reader = csv.DictReader(f, delimiter=delimiter)
    return list(reader)

def parse_year(date_str):
# Extract year from bookmark date.
# Expected format: '03 Jan 2026'
  if not date_str:
    return None
  try:
    return datetime.strptime(date_str.strip(), "%d %b %Y").year
  except ValueError:
    raise ValueError(f"Unrecognized bookmark date format: {date_str}")

def split_field(field):
# Split comma-separated CSV fields into clean lists.
  if not field:
    return []
  return [x.strip() for x in field.split(",") if x.strip()]

def toEnglish(a):
  return unidecode(a)

def splitString(a, maxl):
  ret = [a]
  while len(ret[-1]) > maxl:
    curr_str = ret[-1]
    first_space = maxl
    while first_space > 0 and curr_str[first_space] != ' ':
      first_space -= 1
    if first_space == 0:
      ret[-1] = curr_str[:maxl-2] + '..\n'
      ret.append(curr_str[maxl-2:])
    else:
      ret[-1] = curr_str[:first_space] + '\n'
      ret.append(curr_str[first_space+1:])
  return "".join(ret)

def splitFandom(a):
  return a.replace(' | ', ' |\n', 1)

def splitShip(ship):
  if "/" in ship:
      i = ship.index('/')
      return toEnglish(ship[:i+1]) + '\n' + toEnglish(ship[i+1:])
  if "&" in ship:
      i = ship.index('&')
      return toEnglish(ship[:i+1]) + '\n' + toEnglish(ship[i+1:])
  return splitString(ship, 20)

def splitAU(AU):
  i = AU.index('-')
  return AU[:i+1] + '\n' + AU[i+1:]

# %%

# Code Cell #4


rows = load_bookmarks_csv(BOOKMARK_CSV_PATH)
fics = []

for row in rows:
  year = parse_year(row["bookmark date"])
  if year != wrapped_year:
    continue
  if row["title"] in fics_to_exclude:
    continue
  if any(author in row["author"] for author in authors_to_exclude):
    continue
  fic = Fic(
      link=row["link"],
      title=row["title"],
      rating=row["rating"],
      authors=split_field(row["author"]),
      fandoms=split_field(row["fandoms"]),
      language="",  # not provided by CSV
      relationships=split_field(row["relationships"]),
      characters=split_field(row["characters"]),
      freeforms=split_field(row["freeforms"]),
      words=int(row["words"]) if row["words"].isdigit() else 0
  )
  fics.append(fic)

fics = list(set(fics))

print("Total fics in wrapped year:", len(fics))

# %%

# Code Cell #5

total_fics = len(fics)
word_counts = [fic.words for fic in fics]
total_words = np.sum(word_counts)

# Longest fic
longest_fic = fics[np.argmax(word_counts)] if fics else None

def find_top(flattened_list, num):
    c = Counter(flattened_list)
    if len(flattened_list) > num:
        return c.most_common(num)
    else:
        return c.most_common()

def find_top_authors(fics, num):
    flat_authors = [author for fic in fics for author in fic.authors]
    filtered = [
        author for author in flat_authors
        if author not in ["orphan_account", "Anonymous"]
    ]
    c = Counter(filtered)
    if len(filtered) > num:
        return c.most_common(num)
    else:
        return c.most_common()

# Rankings

top5Authors = find_top_authors(fics, 5)
favCharacters = find_top([char for fic in fics for char in fic.characters], 2)
top4Fandoms = find_top([fandom for fic in fics for fandom in fic.fandoms], 4)
top5Tags = find_top([tag for fic in fics for tag in fic.freeforms], 5)
favRating = find_top([fic.rating for fic in fics], 3)
favShips = find_top([rel for fic in fics for rel in fic.relationships], 10)

# Longest fics (top 5)
sorted_fics_wc = sorted(fics, key=lambda fic: fic.words, reverse=True)
top_5_by_wc = sorted_fics_wc[:5]
longest5Fics = [(fic.title, fic.words) for fic in top_5_by_wc]

print("Total fics:", total_fics)
print("Total words:", total_words)
print("Favorite authors:", top5Authors)
print("Favorite characters:", favCharacters)
print("Favorite fandoms:", top4Fandoms)
print("Favorite tags:", top5Tags)
print("Favorite rating:", favRating)
print("Favorite ships:", favShips)
print("Longest fics:", longest5Fics)

# %%

# Code Cell #6
def commentRating(favR):
    if favR == 'Explicit':
        com = "No judgement."
    elif favR == 'Mature':
        com = "You're a little spicy."
    elif favR == 'Teen And Up Audiences':
        com = "Jesus is proud."
    elif favR == 'General Audiences':
        com = "We love to see it!"
    else:
        com = ""
    return com


def commentWords(wordsTot):
    if wordsTot < 50000:
        com = "Congrats, it seems that you touch grass."
    elif wordsTot < 120000:
        com = "That's a whole novel!"
    elif wordsTot < 250000:
        com = "That's almost the longest \nHarry Potter book!"
    elif wordsTot < 320000:
        com = "Look at that, that could be \na A Song of Ice and Fire book!"
    elif wordsTot < 450000:
        com = "You've almost finished \nthe Earthsea series!"
    elif wordsTot < 600000:
        com = "That's almost the equivalent \nof the Lord of the Ring series!"
    elif wordsTot < 1000000:
        com = "That's almost the equivalent \nof the Harry Potter series!"
    elif wordsTot < 1800000:
        com = "That's almost the equivalent \nof the Song of Ice & Fire series!"
    else:
        com = f"Wow, that's about {wordsTot//365} words a day."
    return com


def commentLength(l):
    if l >= 1000 and l <= 5000:
        com = "You're more of a oneshot \nkind of person."
    elif l < 50000:
        com = "Hey, that's the \naverage length of a novella!"
    elif l < 100000:
        com = "That's around the length of \nof the first Harry Potter book!"
    elif l < 120000:
        com = "Good job, you've basically \nread a large novel!"
    elif l > 120000:
        com = "This one is longer \nthan your average novel!"
    elif l > 1000000:
        com = "Wow, that's one dedicated author."
    else:
        com = ""
    return com


def commentTrope(trope):
    if trope in ['Not Canon Compliant', 'Alternate Universe - Canon Divergence']:
        com = "Canon? What canon?"
    elif trope == 'Fluff':
        com = "I see you're keeping your dentist busy."
    elif trope in [
        'Angst', 'Hurt No Comfort', 'Whump', 'Death', 'Violence',
        'Blood', 'Abuse', 'Hurt', 'Character Death'
    ]:
        com = "...Are you okay, friend?"
    elif trope in [
        'Sexual Content', 'Sex', 'Smut', 'Oral Sex', 'Anal Sex',
        'Anal', 'BDSM', 'Porn', 'Bottoming'
    ]:
        com = "Bonk??"
    elif trope == 'Hurt/Comfort':
        com = "... emphasis on Comfort."
    elif trope == 'Getting Together':
        com = "Fucking finally!"
    elif trope in ['Humor', 'Crack', 'Light-Hearted']:
        com = "Better laugh than cry, right?"
    elif trope == 'Established Relationship':
        com = "Ah yes, we love the domesticity."
    elif trope in ['Happy Ending', 'Angst with a Happy Ending']:
        com = "We all need the happy ending."
    elif trope == 'One Shot':
        com = "Make it short!"
    elif trope in ['Slow Burn', 'Pining', 'Friends to Lovers']:
        com = "I can smell the pine trees from here."
    elif trope == 'Plot What Plot/Porn Without Plot':
        com = "Who needs plot?"
    elif trope in ['Fluff and Angst', 'Fluff and Smut']:
        com = "Because why not both?"
    elif trope == 'Enemies to Lovers':
        com = "Ohh, you wanna kiss me so bad."
    elif trope in [
        'Alternate Universe - College/University',
        'University',
        'Canon Compliant'
    ]:
        com = "An entire world of fiction, and this is where you go."
    elif trope == 'Alpha/Beta/Omega Dynamics':
        com = "Hey, it's knot anything to be ashamed of."
    elif trope == 'Dead Dove: Do Not Eat':
        com = "Close that fridge!"
    elif trope == 'Incest':
        com = "Sweet Home Alabama"
    else:
        com = "Never gets old."
    return com

com_wordsTot = commentWords(total_words)
com_rating = commentRating(favRating[0][0])
com_longest = commentLength(longest_fic.words)
com_trope = commentTrope(top5Tags[0][0])

# %%

# Code Cell #7

fontBig = ImageFont.truetype("/content/AO3_wrapped_blank_images/LeagueSpartan-Bold.ttf", 150)
fontMed = ImageFont.truetype("/content/AO3_wrapped_blank_images/LeagueSpartan-Bold.ttf", 70)
fontSmall = ImageFont.truetype("/content/AO3_wrapped_blank_images/LeagueSpartan-Bold.ttf", 50)
fontSmallish = ImageFont.truetype("/content/AO3_wrapped_blank_images/LeagueSpartan-Bold.ttf", 40)
fontSmaller = ImageFont.truetype("/content/AO3_wrapped_blank_images/LeagueSpartan-Bold.ttf", 30)

fontMed_maxLetters = 19

red = (151, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)

gap_small = 30
gap = 45
gap_large = 70

# %%

# Code Cell #8 (Page 1 - Overview)
image1 = Image.open("/content/AO3_wrapped_blank_images/1.png")
imgW, imgH = image1.size

d1 = ImageDraw.Draw(image1)

P1_LEFT   = 100
P1_RIGHT  = 975
P1_TOP    = 390
P1_BOTTOM = 1835

P1_CENTER_X = (P1_LEFT + P1_RIGHT) / 2

# WRAPPED YEAR

d1.text((imgW / 2 - 100 , 280), str(wrapped_year), font=fontSmall, fill=black, anchor="lm")

# HELPER FUNCTION

def draw_text_block(text, font, fill, y, max_chars=None, gap=40):
    if max_chars:
        text = splitString(text, max_chars)

    bbox = d1.multiline_textbbox((0, 0), text, font=font, align="center")
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = P1_CENTER_X - w / 2

    d1.multiline_text((x, y), text, font=font, fill=fill, align="center")

    return y + h + gap

y = P1_TOP + 100

# TOTAL FICS

y = draw_text_block(str(total_fics), fontBig, red, y)

sentence = ("That's the number of\n" "works you've read this\n" "year, amounting to")

y = draw_text_block(sentence, fontMed, black, y)

# TOTAL WORDS

y = draw_text_block(f"{total_words}", fontBig, red, y)

y = draw_text_block("words", fontMed, black, y)

# WORDS COMMENTARY

words_comment = commentWords(total_words)

y = draw_text_block(words_comment, fontSmall, black, y)

# LONGEST FIC

y = draw_text_block("The longest one was", fontMed, black, y)

title_text = splitString(longest_fic.title, 18)
y = draw_text_block(title_text, fontMed, red, y)

# LONGEST FIC AUTHOR

author_text = "by " + ", ".join(longest_fic.authors)

y = draw_text_block(author_text, fontSmall, black, y)

# LONGEST FIC AUTHOR COMMENTARY
length_comment = commentLength(longest_fic.words)

y = draw_text_block(length_comment, fontSmall, black, y)

# SANITY CHECK (OVERFLOW)

if y > P1_BOTTOM:
    print("⚠️ Page 1 content exceeds frame by", y - P1_BOTTOM, "pixels")

image1.save("Page_1_Overview.png", format="PNG")

# %%

# Code Cell #9 (Page 2 - Fandoms & Characters)
image2 = Image.open("/content/AO3_wrapped_blank_images/2.png")
imgW, imgH = image2.size

d2 = ImageDraw.Draw(image2)

Z1_LEFT, Z1_TOP, Z1_RIGHT, Z1_BOTTOM = 90, 300, 810, 515
Z1_CENTER_X = (Z1_LEFT + Z1_RIGHT) / 2
Z1_CENTER_Y = (Z1_TOP + Z1_BOTTOM) / 2

# TOP FANDOMS

intro = "This year, you couldn't\n" "get enough of"

bbox = d2.multiline_textbbox((0, 0), intro, font=fontMed, align="center")
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]

d2.multiline_text((Z1_CENTER_X - w / 2, Z1_CENTER_Y - h / 2), intro, font=fontMed, fill=black, align="center")

main_fandom = splitString(top4Fandoms[0][0], 18)

bbox = d2.multiline_textbbox((0, 0), main_fandom, font=fontMed, align="center")
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]

Z2_LEFT, Z2_TOP, Z2_RIGHT, Z2_BOTTOM = 0, 515, 890, 705
Z2_CENTER_X = (Z2_LEFT + Z2_RIGHT) / 2
Z2_CENTER_Y = (Z2_TOP + Z2_BOTTOM) / 2

d2.multiline_text((Z2_CENTER_X - w / 2, Z2_CENTER_Y - h / 2), main_fandom, font=fontMed, fill=white, align="center")

Z3_LEFT, Z3_TOP, Z3_RIGHT, Z3_BOTTOM = 90, 705, 810, 1355
Z3_CENTER_X = (Z3_LEFT + Z3_RIGHT) / 2

y = Z3_TOP + 50
gapS = 16
gap_ = 24

attached_height = 0

if len(top4Fandoms) > 1:
    text = "along with"
    bbox = d2.textbbox((0, 0), text, font=fontSmall)
    h = bbox[3] - bbox[1]

    d2.text((Z3_CENTER_X, y), text, font=fontMed, fill=black, anchor="mm")

    y += h + gapS
    attached_height += h + gapS

    second_fandom = splitString(top4Fandoms[1][0], 26)
    bbox = d2.multiline_textbbox((0, 0), second_fandom, font=fontSmall, align="center")
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    d2.multiline_text((Z3_CENTER_X - w / 2, y), second_fandom, font=fontSmall, fill=red, align="center")

    y += h + gap_
    attached_height += h + gap_

# FAVORITE CHARACTER

center_blocks = [
    ("& you've been\nobsessed with", fontMed, black),
    (splitString(favCharacters[0][0], 22), fontMed, red),
    (f"who appears in {favCharacters[0][1]} works", fontSmall, black),
]

gapC = 24
total_center_height = 0
measured = []

for text, font, color in center_blocks:
    bbox = d2.multiline_textbbox((0, 0), text, font=font, align="center")
    h = bbox[3] - bbox[1]
    measured.append((text, font, color, h))
    total_center_height += h

total_center_height += gapC * (len(measured) - 1)

remaining_top = Z3_TOP + attached_height
remaining_height = Z3_BOTTOM - remaining_top

y = remaining_top + (remaining_height - total_center_height) / 2

for text, font, color, h in measured:
    bbox = d2.multiline_textbbox((0, 0), text, font=font, align="center")
    w = bbox[2] - bbox[0]

    d2.multiline_text(
        (Z3_CENTER_X - w / 2, y),
        text,
        font=font,
        fill=color,
        align="center"
    )

    y += h + gapC

image2.save("Page_2_Fandoms_&_Characters.png", format="PNG")

# %%

# Code Cell #1O (Page 3 - Ships & Authors)

image3 = Image.open("/content/AO3_wrapped_blank_images/3.png")
d3 = ImageDraw.Draw(image3)

steps = [
    # (left, top, right, bottom)
    (0,   415, 300, 590),
    (300, 590, 566, 730),
    (566, 730, 900, 880),
]

AUTHORS_LEFT_X = 0
AUTHORS_TOP_Y = 900
AUTHORS_RIGHT_X = 900
AUTHORS_BOTTOM_Y = 1500

top_ships = favShips[:3]  # [(ship_name, count), ...]

for i, (left, top, right, bottom) in enumerate(steps):
    if i >= len(top_ships):
        break

    ship_name, count = top_ships[i]

    # ---- Draw "XX fics" centered in red block ----
    fics_text = f"{count} fics"

    bbox = d3.textbbox((0, 0), fics_text, font=fontSmall)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2

    d3.text(
        (center_x - w / 2, center_y - h / 2),
        fics_text,
        font=fontSmall,
        fill=white
    )

    # ---- Draw ship name (left-anchored) ----
    ship_text = splitShip(ship_name)

    text_x = left + 20   # padding from left edge
    text_y = top - 120 if i == 0 else top - 100 # above the block

    if i == 0:
      ship_font = fontMed
    if i == 1:
      ship_font = fontSmall
    if i ==2:
      ship_font = fontSmaller

    d3.multiline_text(
        (text_x, text_y),
        ship_text,
        font=ship_font,
        fill=black,
        align="left"
    )

authors_blocks = []

# Title line
authors_blocks.append(
    ("You can thank your most \n"" read authors for that", fontMed, white)
)

# Author usernames
for author, _ in top5Authors:
    authors_blocks.append((author, fontSmall, black))

gap_title = 30   # space AFTER the title
gap_author = 10  # space BETWEEN authors

total_height = 0
measured = []

for text, font, color in authors_blocks:
    bbox = d3.multiline_textbbox((0, 0), text, font=font, align="center")
    h = bbox[3] - bbox[1]
    measured.append((text, font, color, h))
    total_height += h

# Add spacing: 1 title gap + (N-2) author gaps
if len(measured) > 1:
    total_height += gap_title
    total_height += gap_author * (len(measured) - 2)

authors_center_x = (AUTHORS_LEFT_X + AUTHORS_RIGHT_X) / 2
authors_height = AUTHORS_BOTTOM_Y - AUTHORS_TOP_Y

y = AUTHORS_TOP_Y + (authors_height - total_height) / 2

for i, (text, font, color, h) in enumerate(measured):
    bbox = d3.multiline_textbbox((0, 0), text, font=font, align="center")
    w = bbox[2] - bbox[0]

    d3.multiline_text(
        (authors_center_x - w / 2, y),
        text,
        font=font,
        fill=color,
        align="center"
    )

    # Bigger gap after title, smaller gaps after authors
    if i == 0:
        y += h + gap_title
    else:
        y += h + gap_author

image3.save("Page_3_Ships_&_Authors.png", format="PNG")

# %%

# Code Cell #11 (Page 4 - Tags)
image4 = Image.open('/content/AO3_wrapped_blank_images/4.png')
imgW, imgH = image4.size
d4 = ImageDraw.Draw(image4)

## ---------
text1 = top5Tags[0][0]
if '-' in text1:
  text1 = splitAU(text1)
elif '/' in text1:
  text1 = splitShip(text1)
elif len(text1) > 20:
   text1 = splitString(text1, 20)

left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text1, font=fontMed)
w, h = right - left, top - bottom
d4.text((650, 400-h/2), text1, font=fontMed, fill =red, anchor ="mm")

text = "with " + str(top5Tags[0][1]) + " works"
left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text, font=fontSmall)
w, h = right - left, top - bottom
d4.text((500, 500-h/2), text, font=fontSmall, fill =(0,0,0))

text2 = splitString(com_trope, 20)
left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text2, font=fontSmall)
w, h = right - left, top - bottom
d4.text((670- w/2, 580-h/2), text2, font=fontSmall, fill =(0,0,0))

## ---------

if len(top5Tags) > 1:

  text3 = top5Tags[1][0]
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text3, font=fontSmall)
  w, h = right - left, top - bottom
  if '-' in text3:
    text3 = splitAU(text3)
  elif '/' in text3:
    text3 = splitShip(text3)
  elif len(text3) > 20:
    text3 = splitString(text3, 20)

  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text3, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((770, 880-h/2), text3, font=fontSmall, fill =red, anchor ="mm")

if len(top5Tags) > 2:

  text4 = top5Tags[2][0]
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text4, font=fontSmall)
  w, h = right - left, top - bottom
  if '-' in text4:
    text4 = splitAU(text4)
  elif '/' in text4:
    text4 = splitShip(text4)
  elif len(text4) > 20:
    text4 = splitString(text4, 20)

  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text4, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((700, 1170-h/2), text4, font=fontSmall, fill =red, anchor ="mm")

if len(top5Tags) > 3:

  text5 = top5Tags[3][0]
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text5, font=fontSmall)
  w, h = right - left, top - bottom
  if '-' in text5:
    text5 = splitAU(text5)
  elif '/' in text5:
    text5 = splitShip(text5)
  elif len(text5) > 20:
    text5 = splitString(text5, 20)

  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text5, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((600, 1420-h/2), text5, font=fontSmall, fill =red, anchor ="mm")

## ---------

if len(top5Tags) > 1:
  text = "with " + str(top5Tags[1][1]) + " works"
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((580, 960-h/2), text, font=fontSmall, fill =(0,0,0))

if len(top5Tags) > 2:

  text = "with " + str(top5Tags[2][1]) + " works"
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((500, 1250-h/2), text, font=fontSmall, fill =(0,0,0))

if len(top5Tags) > 3:

  text = "with " + str(top5Tags[3][1]) + " works"
  left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text, font=fontSmall)
  w, h = right - left, top - bottom
  d4.text((420, 1490-h/2), text, font=fontSmall, fill =(0,0,0))

## ---------
text6 = favRating[0][0]
if  text6 == 'Teen And Up Audiences':
  text6 = text6[:12] + "\n" +  text6[12:]

left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text6, font=fontMed)
w, h = right - left, top - bottom
d4.text((300- w/2, 1690-h/2), text6, font=fontMed, fill =(250,250,250))

text7 = "that's " + str(favRating[0][1]) + " works."
left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text7, font=fontSmall)
w, h = right - left, top - bottom
d4.text((570, 1750-h/2), text7, font=fontSmall, fill =(0,0,0))

text8 = com_rating
left, top, right, bottom = d4.textbbox( [imgW/2,imgH/2], text8, font=fontSmall)
w, h = right - left, top - bottom
d4.text((570, 1800-h/2), text8, font=fontSmall, fill =(0,0,0))


image4.save("Page_4_Tags.png", format='PNG')
