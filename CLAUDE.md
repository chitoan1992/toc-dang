# Tộc Đặng Non Nước Family Tree Project

## Project Overview

Family tree website for **Tộc Đặng Non Nước** - a lineage in Đà Nẵng, Vietnam with over 500 years of history.

- **Total members:** 3,366 people
- **Generations:** 14 (Đời 1-14)
- **Founder:** Đặng Văn Cẩn (born 1519-10-20)
- **Contact:** admin@tocdangnonnuoc.com

## Project Structure

```
toc-dang/
├── src/                          # Python scripts
│   ├── convert_to_json.py        # FamilyScript → JSON converter
│   ├── extract_images.py         # Extract photos from HTML
│   ├── analyze_generations.py   # Analyze generation data
│   ├── detailed_analysis.py     # Find data errors
│   └── find_negative_generations.py
├── docs/                         # Web files (GitHub Pages)
│   ├── index.html               # Main family viewer
│   ├── family-tree.html         # Source data from Family Echo
│   ├── family_data.json         # Full family data (2.8 MB)
│   ├── family_data.min.json     # Minified version (1.9 MB)
│   ├── family_tree.json         # Tree structure for D3.js (1.3 MB)
│   └── photos_map.json          # Photo mapping (590 KB)
└── CLAUDE.md                    # This file

```

## Data Files

### Source Data
- `docs/family-tree.html` - Interactive HTML from Family Echo (3 MB)
  - Contains FamilyScript data in embedded script
  - 67 photos embedded as base64
  - Source of truth for all data

### Generated Data (auto-generated, don't edit manually)
- `docs/family_data.json` - Full family data with relationships
- `docs/family_data.min.json` - Minified for web performance
- `docs/family_tree.json` - Hierarchical tree structure for D3.js
- `docs/photos_map.json` - Photo data extracted from HTML

## Scripts

All scripts should be run from project root directory.

### Convert FamilyScript to JSON
```bash
python3 src/convert_to_json.py docs/family-tree.html -o docs
```

**What it does:**
- Parses FamilyScript format from HTML
- Builds family relationships (parents/children/spouses)
- Infers generation numbers from relationships (72.8% auto-inferred)
- Exports JSON files to docs/ folder

### Extract Photos
```bash
python3 src/extract_images.py
```

**What it does:**
- Extracts 67 base64 photos from family-tree.html
- Creates photos_map.json for web viewer
- Updates family_data_with_photos.json

### Analyze Data Quality
```bash
python3 src/analyze_generations.py       # Generation analysis
python3 src/detailed_analysis.py          # Find data errors
python3 src/find_negative_generations.py  # Find invalid generations
```

## Data Format

### FamilyScript (from Family Echo)

Each line is one person starting with `i<ID>`:

```
i<ID>    = Person ID
f<ID>    = Father ID
m<ID>    = Mother ID
s<ID>    = Spouse ID
p<name>  = First name
l<name>  = Surname
q<name>  = Surname at birth
g<m/f>   = Gender (m=male, f=female)
b<date>  = Birth date (YYYYMMDD)
d<date>  = Death date
z1       = Is deceased
a<addr>  = Address
e<email> = Email
u<phone> = Phone
o<text>  = Bio notes (contains generation info)
r<img>   = Photo (base64)
```

**Example:**
```
iSTART	b15191020	gm	pCẩn	lĐặng Văn	oĐời thứ 1,Đặng Văn Non nước
```

### JSON Structure

```json
{
  "metadata": {
    "family_name": "Tộc Đặng Non Nước",
    "total_members": 3366,
    "total_families": 595
  },
  "persons": {
    "START": {
      "id": "START",
      "firstName": "Cẩn",
      "surname": "Đặng Văn",
      "gender": "male",
      "birthDate": "1519-10-20",
      "generation": 1,
      "fatherId": null,
      "motherId": null,
      "spouseIds": ["T840G"],
      "childrenIds": ["N72F1", "CV3C9", "K2TAC"],
      "notes": "Đời thứ 1, Đặng Văn Non nước"
    }
  },
  "families": { ... }
}
```

## Web Interface (docs/index.html)

Interactive family tree viewer:
- D3.js visualization
- Search and filter (by generation, gender, status)
- Person detail panel
- Photo support
- Responsive design

## Coding Guidelines

### When working with data:

1. **Source of truth:** `docs/family-tree.html` is the original data
2. **Auto-generated files:** Never edit JSON files manually - regenerate from source
3. **Workflow:** Edit family-tree.html → Run scripts → Test in browser

### When updating scripts:

1. **Keep it simple:** Follow YAGNI principle
2. **Run from root:** Scripts assume CWD is project root
3. **Relative paths:** Use `docs/` prefix for all data files
4. **Test after changes:** Run script and verify JSON output

### When updating web interface:

1. **Main file:** `docs/index.html`
2. **Data loading:** Fetches `family_data.json` and `photos_map.json`
3. **Test locally:** `python3 -m http.server 8000` then open `http://localhost:8000/docs/`

## Common Tasks

### Update family data from Family Echo:
1. Download new HTML from Family Echo
2. Replace `docs/family-tree.html`
3. Run: `python3 src/convert_to_json.py docs/family-tree.html -o docs`
4. Run: `python3 src/extract_images.py`
5. Commit and push to GitHub

### Add new features to web viewer:
1. Edit `docs/index.html`
2. Test locally with: `python3 -m http.server 8000`
3. Open: `http://localhost:8000/docs/`
4. Commit and push to GitHub

### Debug data issues:
1. Run analysis scripts to find errors
2. Fix in Family Echo website
3. Re-export and regenerate JSON

## Known Issues

### Data Quality
- 150 people with undetermined generation (4.5%)
- 3 parent-child generation mismatches (documented in project-description.md)
- 88 people with invalid names (empty or single character)

### Generation Inference
- 22.7% have explicit generation info
- 72.8% inferred from relationships (parent → child = +1 generation)
- 4.5% cannot be determined (no links to known generations)

## Deployment

- **Platform:** GitHub Pages
- **URL:** https://[username].github.io/toc-dang/docs/
- **Auto-deploy:** Push to master branch
- **Files served:** Everything in `docs/` folder

---

**Last updated:** 2026-02-01
**Maintainer:** Đặng Toàn
