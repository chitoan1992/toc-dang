#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích chi tiết và tìm tất cả các lỗi dữ liệu
"""

import re
from collections import defaultdict

def parse_familyscript(filepath):
    """Parse FamilyScript file"""
    persons = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('i'):
                continue

            match = re.match(r'^i([A-Z0-9]+)\t', line)
            if not match:
                continue

            person_id = match.group(1)
            person = {
                'id': person_id,
                'name': '',
                'surname': '',
                'father_id': None,
                'mother_id': None,
                'generation': None,
                'raw_line': line
            }

            fields = line.split('\t')
            for field in fields[1:]:
                if field.startswith('p'):
                    person['name'] = field[1:]
                elif field.startswith('l'):
                    person['surname'] = field[1:]
                elif field.startswith('f'):
                    person['father_id'] = field[1:]
                elif field.startswith('m') and len(field) > 1 and field[1].isupper():
                    person['mother_id'] = field[1:]
                elif field.startswith('o') or field.startswith('A'):
                    text = field[1:]
                    gen_match = re.search(r'[Đđ]ời\s*[Tt]hứ\s*(\d+)', text)
                    if gen_match:
                        person['generation'] = int(gen_match.group(1))

            persons[person_id] = person

    return persons


def find_all_errors(persons):
    """Find all data quality issues"""

    errors = []

    # 1. Check parent-child generation consistency
    for pid, person in persons.items():
        if person['father_id'] and person['father_id'] in persons:
            father = persons[person['father_id']]
            if person['generation'] and father['generation']:
                expected = father['generation'] + 1
                if person['generation'] != expected:
                    errors.append({
                        'type': 'GEN_MISMATCH',
                        'severity': 'HIGH',
                        'person_id': pid,
                        'person_name': f"{person['name']} {person['surname']}",
                        'person_gen': person['generation'],
                        'father_id': person['father_id'],
                        'father_name': f"{father['name']} {father['surname']}",
                        'father_gen': father['generation'],
                        'expected_gen': expected,
                        'message': f"Con {person['name']} ghi Đời {person['generation']} nhưng cha {father['name']} là Đời {father['generation']} → Con phải là Đời {expected}"
                    })

    # 2. Check for orphaned records (no family links)
    for pid, person in persons.items():
        has_father = person['father_id'] and person['father_id'] in persons
        has_mother = person['mother_id'] and person['mother_id'] in persons

        # Check if this person is a parent of anyone
        is_parent = False
        for other_pid, other in persons.items():
            if other['father_id'] == pid or other['mother_id'] == pid:
                is_parent = True
                break

        if not has_father and not has_mother and not is_parent and pid != 'START':
            if 'Đặng' in person.get('surname', ''):
                errors.append({
                    'type': 'ORPHAN',
                    'severity': 'MEDIUM',
                    'person_id': pid,
                    'person_name': f"{person['name']} {person['surname']}",
                    'message': f"{person['name']} {person['surname']} không có liên kết với ai trong gia phả"
                })

    # 3. Check for missing names
    for pid, person in persons.items():
        if not person['name'] or person['name'] in ['A', 'B', 'C', 'Y', 'Vợ']:
            errors.append({
                'type': 'INVALID_NAME',
                'severity': 'HIGH',
                'person_id': pid,
                'person_name': f"{person['name']} {person['surname']}",
                'message': f"Tên không hợp lệ: '{person['name']}'"
            })

    return errors


def print_report(errors, persons):
    """Print detailed error report"""

    print("=" * 80)
    print("BÁO CÁO CHI TIẾT CÁC LỖI DỮ LIỆU GIA PHẢ")
    print("=" * 80)

    # Group by type
    by_type = defaultdict(list)
    for e in errors:
        by_type[e['type']].append(e)

    # 1. Generation mismatches
    print("\n" + "=" * 80)
    print("1. LỖI KHÔNG KHỚP THÔNG TIN ĐỜI (Con và Cha)")
    print("=" * 80)

    gen_errors = by_type.get('GEN_MISMATCH', [])
    if gen_errors:
        print(f"\nTìm thấy {len(gen_errors)} lỗi:\n")
        for e in gen_errors:
            print(f"❌ {e['message']}")
            print(f"   ID Con: {e['person_id']}, ID Cha: {e['father_id']}")
            print()
    else:
        print("\n✅ Không tìm thấy lỗi")

    # 2. Invalid names
    print("\n" + "=" * 80)
    print("2. TÊN KHÔNG HỢP LỆ")
    print("=" * 80)

    name_errors = by_type.get('INVALID_NAME', [])
    if name_errors:
        print(f"\nTìm thấy {len(name_errors)} tên không hợp lệ:\n")
        for e in name_errors:
            p = persons[e['person_id']]
            father_info = ""
            if p['father_id'] and p['father_id'] in persons:
                f = persons[p['father_id']]
                father_info = f"Cha: {f['name']} {f['surname']}"

            print(f"❌ {e['person_name']}")
            print(f"   ID: {e['person_id']} | {father_info or 'Không có thông tin cha'}")
    else:
        print("\n✅ Không tìm thấy lỗi")

    # 3. Orphans
    print("\n" + "=" * 80)
    print("3. NGƯỜI KHÔNG CÓ LIÊN KẾT GIA ĐÌNH (Họ Đặng)")
    print("=" * 80)

    orphan_errors = by_type.get('ORPHAN', [])
    if orphan_errors:
        print(f"\nTìm thấy {len(orphan_errors)} người:\n")
        for e in orphan_errors[:30]:  # Limit to 30
            print(f"⚠️  {e['person_name']} (ID: {e['person_id']})")
        if len(orphan_errors) > 30:
            print(f"\n... và {len(orphan_errors) - 30} người khác")
    else:
        print("\n✅ Không tìm thấy")

    # Summary
    print("\n" + "=" * 80)
    print("TÓM TẮT")
    print("=" * 80)
    print(f"\nTổng số người: {len(persons)}")
    print(f"Lỗi đời không khớp: {len(gen_errors)} (CẦN SỬA NGAY)")
    print(f"Tên không hợp lệ: {len(name_errors)} (CẦN SỬA)")
    print(f"Người không liên kết: {len(orphan_errors)} (NÊN KIỂM TRA)")


if __name__ == "__main__":
    input_file = "/Users/toandang/Downloads/FamilyEcho/My-Family-20-Jan-2026-020424519.txt"

    persons = parse_familyscript(input_file)
    errors = find_all_errors(persons)
    print_report(errors, persons)
