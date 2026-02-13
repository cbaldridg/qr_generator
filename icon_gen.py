import os

# The SVG content as a multi-line string
bag_icon_svg = """<svg width="100" height="120" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 45 L80 45 L 75 95 Q 74 105 60 105 L 40 105 Q 26 105 25 95 L 20 45 Z" stroke="black" stroke-width="5" stroke-linejoin="round"/>
  <path d="M38 45 V 25 Q 38 20 43 20 H 57 Q 62 20 62 25 V 45" stroke="black" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="38" cy="50" r="3" fill="black"/>
  <circle cx="62" cy="50" r="3" fill="black"/>
</svg>"""

# Example 1: Function to return the SVG string (e.g., for a web framework like Flask/Django)
def get_bag_icon():
    return bag_icon_svg

# Example 2: Saving the SVG to a file
def save_icon(filename="bag_icon.svg"):
    with open(filename, "w") as f:
        f.write(bag_icon_svg)
    print(f"Successfully saved {filename}")

if __name__ == "__main__":
    save_icon()