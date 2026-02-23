# Welcome to AO3 Wrapped!
This is a fan-made, Spotify Wrapped–style recap of your Archive of Our Own reading habits.

## Credits and Inspiration

All credit goes to **@kyucultures** on X (soupbanana on GitHub) for creating the original AO3 Wrapped project :)

Her version generates a Wrapped based on your **AO3 reading history** (everything you clicked on). While that works great for many people, I personally found it a bit inaccurate for my own reading habits (I click on a lot of fics I don’t actually finish).

Because of that, this version uses **bookmarks instead of history**, under the assumption that I bookmark every work I finished (which i started doing at the start of last year, thankfully).

Here's the original reddit post where I found the project: https://www.reddit.com/r/AO3/comments/1h6xlic/ao3_wrapped/

## Instructions
(Please note: you need a computer, doing it on your phone would be very difficult.)

### Step 1: Export you AO3 bookmarks

The most tiresome part of this project is exporting your bookmarks from AO3, since the platform does not currently offer a built-in way to export bookmarks as a CSV.

To do this, I used the bookmarklets from this website:
https://random.fangirling.net/scripts/ao3_works_stats/

(For more instructions as to how it works, go to this page: https://random.fangirling.net/scripts/how_to_use_bookmarklets/)

I recommend using Chrome for this process.

*(I know exporting the history page by page is annoying but stick with it. If you're like me and love accurate statistical data, it's worth it)*

### Step 2: Combine the CSV files

One downside of this method is that it generates one CSV file per bookmarks page.

In my case, I had 28 pages, so merging them by hand took a long time (yes, I did it…).

After confirming that the project worked, I looked for automatic CSV mergers and found this one to work best: https://csvcombiner.com/

When using it, make sure to check "Files include headers", "Skip empty rows" and "Remove duplicate rows (must be exact)".

### Step 3: Configure the notebook

Upload the merged bookmarks CSV file into your notebook environment (📁 icon).

In **Code Cell #1**, set:
*   the path to your CSV file
*   the year you want to generate your Wrapped for
* optional exclusions (titles or authors)

Example:
```
BOOKMARK_CSV_PATH = "/content/Stats.csv"
wrapped_year = 2025
```

### Step 4: Run the notebook
Click "Run all".

The four images will appear in the file browser (📁 icon).


**Happy reading, and enjoy your AO3 Wrapped!**
