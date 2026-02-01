#!/usr/bin/env python3
"""
Extract images from FamilyEcho HTML and create a mapping to person IDs.
Updates family_data.json with photo information.
"""

import re
import json
import os

def extract_images_from_html(html_file):
    """Extract all base64 images from HTML file."""
    print(f"Reading {html_file}...")

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all image tags with base64 data
    # Format: <IMG WIDTH=0 HEIGHT=0 STYLE="display:none;" ID="image-754551379" SRC="data:image/jpeg;base64,...">
    image_pattern = r'ID="image-(\d+)"\s+SRC="(data:image/[^;]+;base64,[^"]+)"'

    images = {}
    matches = re.findall(image_pattern, content)

    for image_id, data_url in matches:
        images[image_id] = data_url

    print(f"Found {len(images)} images")
    return images

def extract_person_photos_from_html(html_file):
    """Extract person to photo mapping from FamilyScript data in HTML."""

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find person lines with photo reference
    # Format: iSTART ... r754551379 160 118 ...
    # The 'r' field contains: image_id width height

    person_photos = {}

    # Pattern to match person lines with photo info
    # Person ID starts with 'i', photo info is 'r' followed by numbers
    person_pattern = r'^i([A-Z0-9]+)\t.*?r(\d+)\s+(\d+)\s+(\d+)'

    for line in content.split('\n'):
        if line.startswith('i') and '\tr' in line:
            # Extract person ID
            parts = line.split('\t')
            if parts:
                person_id = parts[0][1:]  # Remove leading 'i'

                # Find photo reference
                for part in parts:
                    if part.startswith('r') and ' ' in part:
                        photo_parts = part[1:].split()
                        if len(photo_parts) >= 3:
                            image_id = photo_parts[0]
                            width = int(photo_parts[1])
                            height = int(photo_parts[2])
                            person_photos[person_id] = {
                                'image_id': image_id,
                                'width': width,
                                'height': height
                            }
                            break

    print(f"Found {len(person_photos)} persons with photos")
    return person_photos

def update_family_data(json_file, person_photos, images):
    """Update family_data.json with photo information."""

    print(f"Reading {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for person_id, photo_info in person_photos.items():
        if person_id in data['persons']:
            image_id = photo_info['image_id']
            if image_id in images:
                data['persons'][person_id]['photo'] = {
                    'data_url': images[image_id],
                    'width': photo_info['width'],
                    'height': photo_info['height']
                }
                updated_count += 1

    print(f"Updated {updated_count} persons with photo data")

    # Save updated JSON
    output_file = json_file.replace('.json', '_with_photos.json')
    print(f"Saving to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Also create a separate photos mapping file (lighter weight)
    photos_map = {}
    for person_id, photo_info in person_photos.items():
        image_id = photo_info['image_id']
        if image_id in images:
            photos_map[person_id] = images[image_id]

    photos_file = 'docs/photos_map.json'
    print(f"Saving photos map to {photos_file}...")
    with open(photos_file, 'w', encoding='utf-8') as f:
        json.dump(photos_map, f, ensure_ascii=False)

    print(f"Photos map size: {len(json.dumps(photos_map)) / 1024 / 1024:.2f} MB")

    return output_file, photos_file

def main():
    html_file = 'docs/family-tree.html'
    json_file = 'docs/family_data.json'

    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return

    # Extract images
    images = extract_images_from_html(html_file)

    # Extract person-photo mapping
    person_photos = extract_person_photos_from_html(html_file)

    # Update JSON
    updated_file, photos_file = update_family_data(json_file, person_photos, images)

    print(f"\nDone!")
    print(f"- Updated data: {updated_file}")
    print(f"- Photos map: {photos_file}")

if __name__ == '__main__':
    main()
