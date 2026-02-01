#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích và suy luận thông tin đời từ liên kết gia đình
"""

import re
from collections import defaultdict

def parse_familyscript(filepath):
    """Parse FamilyScript file and extract person data"""
    persons = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('i'):
                continue

            # Extract ID
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
                'gen_source': None,  # 'explicit' or 'inferred'
                'phai': None,
                'chi': None
            }

            # Parse fields
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
                    # Extract generation from notes
                    text = field[1:]
                    gen_match = re.search(r'[Đđ]ời\s*[Tt]hứ\s*(\d+)', text)
                    if gen_match:
                        person['generation'] = int(gen_match.group(1))
                        person['gen_source'] = 'explicit'

                    # Extract Phái
                    phai_match = re.search(r'[Pp]hái\s*([^,\s]+)', text)
                    if phai_match:
                        person['phai'] = phai_match.group(1)

                    # Extract Chi
                    chi_match = re.search(r'[Cc]hi\s*([^,\s]+)', text)
                    if chi_match:
                        person['chi'] = chi_match.group(1)

            persons[person_id] = person

    return persons


def propagate_generations(persons):
    """Propagate generation info from parents to children and vice versa"""

    # Build children index
    children_of = defaultdict(list)
    for pid, person in persons.items():
        if person['father_id'] and person['father_id'] in persons:
            children_of[person['father_id']].append(pid)
        if person['mother_id'] and person['mother_id'] in persons:
            children_of[person['mother_id']].append(pid)

    changes = True
    iterations = 0
    max_iterations = 20

    while changes and iterations < max_iterations:
        changes = False
        iterations += 1

        for pid, person in persons.items():
            if person['generation'] is not None:
                continue

            # Try to infer from father
            if person['father_id'] and person['father_id'] in persons:
                father = persons[person['father_id']]
                if father['generation'] is not None:
                    person['generation'] = father['generation'] + 1
                    person['gen_source'] = f"inferred from father {father['name']} {father['surname']}"
                    changes = True
                    continue

            # Try to infer from mother (if she's a Đặng)
            if person['mother_id'] and person['mother_id'] in persons:
                mother = persons[person['mother_id']]
                if mother['generation'] is not None and 'Đặng' in mother.get('surname', ''):
                    person['generation'] = mother['generation'] + 1
                    person['gen_source'] = f"inferred from mother {mother['name']} {mother['surname']}"
                    changes = True
                    continue

            # Try to infer from children (generation = child's generation - 1)
            for child_id in children_of.get(pid, []):
                child = persons[child_id]
                if child['generation'] is not None:
                    person['generation'] = child['generation'] - 1
                    person['gen_source'] = f"inferred from child {child['name']} {child['surname']}"
                    changes = True
                    break

    return iterations


def analyze_results(persons):
    """Analyze and report results"""

    total = len(persons)
    with_gen = sum(1 for p in persons.values() if p['generation'] is not None)
    explicit = sum(1 for p in persons.values() if p['gen_source'] == 'explicit')
    inferred = sum(1 for p in persons.values() if p['gen_source'] and p['gen_source'].startswith('inferred'))
    without_gen = total - with_gen

    print("=" * 70)
    print("BÁO CÁO PHÂN TÍCH THÔNG TIN ĐỜI")
    print("=" * 70)
    print(f"\nTổng số người trong gia phả: {total}")
    print(f"Có thông tin đời rõ ràng:    {explicit} ({explicit*100/total:.1f}%)")
    print(f"Suy luận được từ liên kết:   {inferred} ({inferred*100/total:.1f}%)")
    print(f"Chưa xác định được đời:      {without_gen} ({without_gen*100/total:.1f}%)")

    # Statistics by generation
    print("\n" + "-" * 70)
    print("THỐNG KÊ THEO ĐỜI")
    print("-" * 70)

    gen_stats = defaultdict(lambda: {'explicit': 0, 'inferred': 0})
    for p in persons.values():
        if p['generation'] is not None:
            if p['gen_source'] == 'explicit':
                gen_stats[p['generation']]['explicit'] += 1
            else:
                gen_stats[p['generation']]['inferred'] += 1

    print(f"{'Đời':<8} {'Rõ ràng':<12} {'Suy luận':<12} {'Tổng':<10}")
    print("-" * 42)
    for gen in sorted(gen_stats.keys()):
        stats = gen_stats[gen]
        total_gen = stats['explicit'] + stats['inferred']
        print(f"Đời {gen:<4} {stats['explicit']:<12} {stats['inferred']:<12} {total_gen:<10}")

    # List people without generation (sample)
    print("\n" + "-" * 70)
    print("MẪU NGƯỜI CHƯA XÁC ĐỊNH ĐƯỢC ĐỜI (20 người đầu)")
    print("-" * 70)

    count = 0
    for pid, p in persons.items():
        if p['generation'] is None and 'Đặng' in p.get('surname', ''):
            father_info = ""
            if p['father_id'] and p['father_id'] in persons:
                f = persons[p['father_id']]
                father_info = f"Cha: {f['name']} {f['surname']}"
                if f['generation']:
                    father_info += f" (Đời {f['generation']})"

            print(f"  - {p['name']} {p['surname']} | {father_info or 'Không có thông tin cha'}")
            count += 1
            if count >= 20:
                break

    # List inferred generations (sample)
    print("\n" + "-" * 70)
    print("MẪU NGƯỜI ĐÃ SUY LUẬN ĐƯỢC ĐỜI (20 người đầu)")
    print("-" * 70)

    count = 0
    for pid, p in persons.items():
        if p['gen_source'] and p['gen_source'].startswith('inferred'):
            print(f"  - {p['name']} {p['surname']}: Đời {p['generation']} ({p['gen_source']})")
            count += 1
            if count >= 20:
                break

    return without_gen


def export_missing_generations(persons, output_file):
    """Export list of people missing generation info"""

    missing = []
    for pid, p in persons.items():
        if p['generation'] is None:
            father_gen = None
            if p['father_id'] and p['father_id'] in persons:
                father_gen = persons[p['father_id']].get('generation')

            missing.append({
                'id': pid,
                'name': f"{p['name']} {p['surname']}",
                'father_id': p['father_id'],
                'father_gen': father_gen,
                'has_dang': 'Đặng' in p.get('surname', '')
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ID\tTên\tCha ID\tĐời cha\tHọ Đặng\n")
        for m in missing:
            f.write(f"{m['id']}\t{m['name']}\t{m['father_id'] or 'N/A'}\t{m['father_gen'] or 'N/A'}\t{'Có' if m['has_dang'] else 'Không'}\n")

    print(f"\nĐã xuất danh sách {len(missing)} người thiếu thông tin đời ra: {output_file}")


if __name__ == "__main__":
    input_file = "/Users/toandang/Downloads/FamilyEcho/My-Family-20-Jan-2026-020424519.txt"
    output_file = "/Users/toandang/Downloads/FamilyEcho/missing_generations.txt"

    print("Đang đọc file FamilyScript...")
    persons = parse_familyscript(input_file)
    print(f"Đã đọc {len(persons)} người")

    print("\nĐang suy luận thông tin đời từ liên kết...")
    iterations = propagate_generations(persons)
    print(f"Hoàn thành sau {iterations} vòng lặp")

    without_gen = analyze_results(persons)

    if without_gen > 0:
        export_missing_generations(persons, output_file)
