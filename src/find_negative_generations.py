#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tìm các liên kết cha-con gây ra đời âm (lỗi dữ liệu)
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
                'generation': None,
            }

            fields = line.split('\t')
            for field in fields[1:]:
                if field.startswith('p'):
                    person['name'] = field[1:]
                elif field.startswith('l'):
                    person['surname'] = field[1:]
                elif field.startswith('f'):
                    person['father_id'] = field[1:]
                elif field.startswith('o') or field.startswith('A'):
                    text = field[1:]
                    gen_match = re.search(r'[Đđ]ời\s*[Tt]hứ\s*(\d+)', text)
                    if gen_match:
                        person['generation'] = int(gen_match.group(1))

            persons[person_id] = person

    return persons


def find_chain_to_founder(persons, person_id, founder_id='START', visited=None):
    """Trace the ancestor chain from a person to the founder"""
    if visited is None:
        visited = set()

    if person_id in visited:
        return None  # Cycle detected

    visited.add(person_id)

    if person_id not in persons:
        return None

    person = persons[person_id]

    if person_id == founder_id:
        return [(person_id, person['name'], person['surname'], person['generation'])]

    if person['father_id']:
        chain = find_chain_to_founder(persons, person['father_id'], founder_id, visited)
        if chain is not None:
            return chain + [(person_id, person['name'], person['surname'], person['generation'])]

    return None


def analyze_negative_generations(persons):
    """Find people with negative inferred generations and trace their lineage"""

    # First, propagate generations
    children_of = defaultdict(list)
    for pid, person in persons.items():
        if person['father_id'] and person['father_id'] in persons:
            children_of[person['father_id']].append(pid)

    gen_map = {}
    for pid, person in persons.items():
        if person['generation'] is not None:
            gen_map[pid] = person['generation']

    # Propagate down from founder
    def propagate_down(pid, parent_gen):
        if pid in gen_map:
            return
        gen_map[pid] = parent_gen + 1
        for child_id in children_of[pid]:
            propagate_down(child_id, parent_gen + 1)

    # Start from people with known generations
    for pid, gen in list(gen_map.items()):
        for child_id in children_of[pid]:
            propagate_down(child_id, gen)

    # Find chains that lead to unexpected results
    print("=" * 80)
    print("PHÂN TÍCH CÁC LIÊN KẾT GÂY RA ĐỜI ÂM")
    print("=" * 80)

    # Find people whose father has a HIGHER generation number (impossible)
    anomalies = []
    for pid, person in persons.items():
        if person['father_id'] and person['father_id'] in persons:
            father = persons[person['father_id']]
            child_gen = person.get('generation') or gen_map.get(pid)
            father_gen = father.get('generation') or gen_map.get(person['father_id'])

            if child_gen and father_gen:
                if child_gen <= father_gen:
                    anomalies.append({
                        'child_id': pid,
                        'child_name': f"{person['name']} {person['surname']}",
                        'child_gen': child_gen,
                        'father_id': person['father_id'],
                        'father_name': f"{father['name']} {father['surname']}",
                        'father_gen': father_gen
                    })

    if anomalies:
        print(f"\nTìm thấy {len(anomalies)} liên kết bất thường (con có đời <= cha):\n")
        for a in anomalies[:20]:
            print(f"  CON: {a['child_name']} (Đời {a['child_gen']})")
            print(f"  CHA: {a['father_name']} (Đời {a['father_gen']})")
            print(f"  --> Lỗi: Con phải có đời = {a['father_gen'] + 1}, không phải {a['child_gen']}")
            print()
    else:
        print("\nKhông tìm thấy liên kết bất thường trực tiếp")

    # Find the specific chain causing negative generations
    # Look for people connected to founder but with wrong generation path
    print("\n" + "-" * 80)
    print("TÌM NGUỒN GỐC CÁC ĐỜI ÂM")
    print("-" * 80)

    # Find people with negative computed generations
    for pid, person in persons.items():
        computed_gen = gen_map.get(pid)
        if computed_gen is not None and computed_gen < 1:
            chain = find_chain_to_founder(persons, pid)
            if chain:
                print(f"\nChuỗi dẫn đến {person['name']} {person['surname']} (tính ra Đời {computed_gen}):")
                for i, (cid, name, surname, explicit_gen) in enumerate(chain):
                    gen_str = f"Đời {explicit_gen}" if explicit_gen else "Không ghi"
                    level = "  " * i
                    expected = i + 1  # Generation should be position in chain
                    print(f"{level}├─ {name} {surname} [{gen_str}] (Đời thực tế: {expected})")

                    # Check for inconsistency
                    if explicit_gen and explicit_gen != expected:
                        print(f"{level}   ⚠️  LỖI: Ghi là Đời {explicit_gen} nhưng phải là Đời {expected}")


if __name__ == "__main__":
    input_file = "/Users/toandang/Downloads/FamilyEcho/My-Family-20-Jan-2026-020424519.txt"

    print("Đang phân tích...")
    persons = parse_familyscript(input_file)
    analyze_negative_generations(persons)
