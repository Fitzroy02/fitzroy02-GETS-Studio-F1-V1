# Community Connectivity & Privacy Charter Infographic

## Overview

This directory contains the Community Connectivity & Privacy Charter infographic, a visual representation of our community guidelines covering four key areas:

1. **Pricing** - Transparent pricing and fee policies
2. **Engagement** - Community interaction rules and guidelines
3. **Meter Usage** - Usage tracking and monitoring policies
4. **Child Oversight** - Parental controls and child safety features

## Files

- `charter_infographic.svg` - Vector SVG source file (editable)
- `charter_infographic_preview.png` - PNG preview/thumbnail (800x1200px)

## Important Update: Engagement Rule

### New Engagement Policy
**Thumbs-up likes can only be given to subscribed members.**

This updated rule is prominently displayed in the Engagement section with a special visual indicator.

### Shield Icon Meaning
The **blue shield with green sapling** icon (🛡️🌱) appears next to the Engagement clause to signify that this feature is exclusive to subscribed members. The shield represents protection and membership status, while the green sapling symbolizes growth and community nurturing.

## Design Specifications

### Colors

The infographic uses a professional, accessible color palette:

- **Background**: `#f8f9fa` (light gray)
- **Title background**: `#2c3e50` (dark blue-gray)
- **Text primary**: `#2c3e50` (dark blue-gray)
- **Text secondary**: `#495057` (medium gray)
- **Section backgrounds**: `#ffffff` (white)
- **Section borders**: `#dee2e6` (light gray)

**Section accent colors:**
- Pricing: `#28a745` (green) 💲
- Engagement: `#007bff` (blue) 👍
- Meter Usage: `#ffc107` (amber) 📊
- Child Oversight: `#dc3545` (red) 🛡️

### Typography

- **Font family**: Arial, sans-serif (system font for maximum compatibility)
- **Title**: 36px, bold
- **Section headings**: 28px, bold
- **Body text**: 16px, regular
- **Footer text**: 14px regular, 12px for copyright

### Accessibility

The infographic has been designed with accessibility in mind:

- **High contrast ratios** - All text meets WCAG AA standards (4.5:1 minimum)
- **Clear hierarchy** - Visual hierarchy using size, weight, and spacing
- **Icon redundancy** - Each section has both icons and text labels
- **Scalable format** - SVG format allows lossless scaling
- **Screen reader friendly** - Semantic text structure in the SVG

### Layout

- **Canvas size**: 800px × 1200px (portrait orientation)
- **Margins**: 40px on all sides
- **Section spacing**: 30px between sections
- **Border radius**: 8px for rounded corners
- **Icon size**: 60px diameter circles

## Editing the SVG

### Using Inkscape (Free, Open Source)

1. **Install Inkscape**: Download from [inkscape.org](https://inkscape.org/)

2. **Open the file**:
   ```bash
   inkscape assets/charter_infographic.svg
   ```

3. **Edit text**: Select the text tool (T) and click on any text element to edit

4. **Modify colors**: Select an element and use the fill/stroke panel (Shift+Ctrl+F)

5. **Adjust layout**: Use the selection tool (S) to move elements

6. **Save**: File → Save (Ctrl+S)

### Using a Text Editor

The SVG is a text-based XML file and can be edited with any text editor:

```bash
nano assets/charter_infographic.svg
# or
code assets/charter_infographic.svg  # VS Code
```

**Key elements to modify:**
- Text content: Look for `<text>` and `<tspan>` elements
- Colors: Modify `fill` and `stroke` attributes
- Positions: Adjust `x`, `y`, `cx`, `cy` attributes
- Sizes: Change `width`, `height`, `r` (radius) attributes

### Using Online Editors

- **Boxy SVG**: [boxy-svg.com](https://boxy-svg.com/)
- **Vectr**: [vectr.com](https://vectr.com/)
- **Method Draw**: [editor.method.ac](https://editor.method.ac/)

## Exporting to Other Formats

### Export to PNG

**Using rsvg-convert (recommended for quality):**

```bash
# Standard preview size (800x1200)
rsvg-convert -w 800 -h 1200 \
  assets/charter_infographic.svg \
  -o assets/charter_infographic_preview.png

# High-resolution version (2x)
rsvg-convert -w 1600 -h 2400 \
  assets/charter_infographic.svg \
  -o assets/charter_infographic_@2x.png

# Thumbnail size (400x600)
rsvg-convert -w 400 -h 600 \
  assets/charter_infographic.svg \
  -o assets/charter_infographic_thumb.png
```

**Using Inkscape:**

```bash
# Export to PNG at 96 DPI
inkscape --export-type=png \
  --export-filename=assets/charter_infographic.png \
  assets/charter_infographic.svg

# Export to PNG at specific size
inkscape --export-type=png \
  --export-width=800 \
  --export-filename=assets/charter_infographic_800.png \
  assets/charter_infographic.svg
```

**Using ImageMagick (convert):**

```bash
convert -density 150 \
  assets/charter_infographic.svg \
  assets/charter_infographic.png
```

### Export to PDF

**Using rsvg-convert:**

```bash
rsvg-convert -f pdf \
  assets/charter_infographic.svg \
  -o assets/charter_infographic.pdf
```

**Using Inkscape:**

```bash
inkscape --export-type=pdf \
  --export-filename=assets/charter_infographic.pdf \
  assets/charter_infographic.svg
```

**Using cairosvg (Python):**

```bash
pip install cairosvg
cairosvg assets/charter_infographic.svg \
  -o assets/charter_infographic.pdf
```

### Export to JPEG

**Using rsvg-convert + ImageMagick:**

```bash
# First convert to PNG, then to JPEG
rsvg-convert -w 800 -h 1200 \
  assets/charter_infographic.svg \
  -o /tmp/charter_temp.png

convert /tmp/charter_temp.png \
  -quality 95 \
  assets/charter_infographic.jpg
```

**Using Inkscape:**

```bash
inkscape --export-type=png \
  --export-filename=/tmp/charter_temp.png \
  assets/charter_infographic.svg

convert /tmp/charter_temp.png \
  -quality 95 \
  assets/charter_infographic.jpg
```

## Installation Requirements

### For rsvg-convert

**Ubuntu/Debian:**
```bash
sudo apt-get install librsvg2-bin
```

**macOS (Homebrew):**
```bash
brew install librsvg
```

**Fedora/RHEL:**
```bash
sudo dnf install librsvg2-tools
```

### For Inkscape

**Ubuntu/Debian:**
```bash
sudo apt-get install inkscape
```

**macOS (Homebrew):**
```bash
brew install --cask inkscape
```

**Windows:**
Download from [inkscape.org/release](https://inkscape.org/release/)

### For ImageMagick

**Ubuntu/Debian:**
```bash
sudo apt-get install imagemagick
```

**macOS (Homebrew):**
```bash
brew install imagemagick
```

## Version History

- **v1.0** (2025-12-10) - Initial release with four charter sections
  - Updated Engagement rule: Thumbs-up likes limited to subscribed members
  - Added blue shield with green sapling icon to indicate subscriber-only features

## Contributing

When updating the infographic:

1. Always edit the SVG source file, not exported versions
2. Test accessibility with a screen reader
3. Verify color contrast meets WCAG standards
4. Export new preview images after making changes
5. Update this README if design specifications change

## License

This infographic is part of the Community Connectivity & Privacy Charter documentation.
Please refer to the main repository LICENSE file for usage terms.

## Questions or Feedback

For questions about the charter infographic or to suggest improvements, please:
- Open an issue in the repository
- Contact the community guidelines team
- Review our CONTRIBUTING.md for contribution guidelines

---

**Last updated**: December 10, 2025
