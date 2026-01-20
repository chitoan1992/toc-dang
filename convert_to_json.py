#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FamilyScript to JSON Converter
Chuyển đổi dữ liệu từ FamilyScript sang JSON cho trang web phả đồ

Tác giả: Tộc Đặng Văn Non Nước
Ngày tạo: 20/01/2026
"""

import re
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class FamilyTreeConverter:
    """Chuyển đổi dữ liệu FamilyScript sang JSON"""

    def __init__(self, input_file: str):
        self.input_file = input_file
        self.persons = {}
        self.families = {}
        self.children_of = defaultdict(list)
        self.spouse_of = defaultdict(list)

    def parse_date(self, date_str: str) -> Optional[Dict]:
        """Parse date string từ FamilyScript (YYYYMMDD format)"""
        if not date_str or len(date_str) < 4:
            return None

        try:
            year = int(date_str[:4]) if len(date_str) >= 4 else None
            month = int(date_str[4:6]) if len(date_str) >= 6 else None
            day = int(date_str[6:8]) if len(date_str) >= 8 else None

            return {
                "year": year,
                "month": month,
                "day": day,
                "display": f"{day or '??'}/{month or '??'}/{year}" if year else None
            }
        except ValueError:
            return None

    def extract_generation(self, text: str) -> Optional[int]:
        """Trích xuất thông tin đời từ text"""
        if not text:
            return None

        # Pattern: "Đời thứ X" hoặc "đời thứ X"
        patterns = [
            r'[Đđ]ời\s*[Tt]hứ\s*(\d+)',
            r'[Đđ]ời\s*(\d+)',
            r'[Gg]en(?:eration)?\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        return None

    def extract_phai(self, text: str) -> Optional[str]:
        """Trích xuất thông tin Phái"""
        if not text:
            return None

        match = re.search(r'[Pp]hái\s+(\w+)', text)
        return match.group(1) if match else None

    def extract_chi(self, text: str) -> Optional[str]:
        """Trích xuất thông tin Chi"""
        if not text:
            return None

        match = re.search(r'[Cc]hi\s+(\d+|\w+)', text)
        return match.group(1) if match else None

    def parse_familyscript(self):
        """Parse file FamilyScript"""
        print(f"Đang đọc file: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Mỗi dòng bắt đầu bằng 'i' là một người
        for line in content.split('\n'):
            line = line.strip()
            if not line.startswith('i'):
                continue

            # Extract ID từ đầu dòng
            match = re.match(r'^i([A-Z0-9]+)\t', line)
            if not match:
                continue

            person_id = match.group(1)
            person = {
                "id": person_id,
                "name": "",
                "surname": "",
                "surname_at_birth": "",
                "gender": None,
                "birth_date": None,
                "birth_place": None,
                "death_date": None,
                "death_place": None,
                "is_deceased": False,
                "burial_place": None,
                "burial_date": None,
                "generation": None,
                "generation_source": None,
                "phai": None,
                "chi": None,
                "father_id": None,
                "mother_id": None,
                "spouse_ids": [],
                "children_ids": [],
                "address": None,
                "email": None,
                "phone": None,
                "photo": None,
                "profession": None,
                "employer": None,
                "interests": None,
                "notes": "",
                "activities": "",
            }

            # Parse các trường
            fields = line.split('\t')
            notes_parts = []

            for field in fields[1:]:
                if not field:
                    continue

                prefix = field[0]
                value = field[1:] if len(field) > 1 else ""

                if prefix == 'p':
                    person["name"] = value
                elif prefix == 'l':
                    person["surname"] = value
                elif prefix == 'q':
                    person["surname_at_birth"] = value
                elif prefix == 'g':
                    person["gender"] = "male" if value == 'm' else "female" if value == 'f' else None
                elif prefix == 'b':
                    person["birth_date"] = self.parse_date(value)
                elif prefix == 'd':
                    person["death_date"] = self.parse_date(value)
                elif prefix == 'z' and value == '1':
                    person["is_deceased"] = True
                elif prefix == 'f':
                    person["father_id"] = value
                elif prefix == 'm' and len(value) > 0 and value[0].isupper():
                    person["mother_id"] = value
                elif prefix == 's':
                    if value and value not in person["spouse_ids"]:
                        person["spouse_ids"].append(value)
                elif prefix == 'a':
                    person["address"] = value
                elif prefix == 'e':
                    person["email"] = value
                elif prefix == 'u':
                    person["phone"] = value
                elif prefix == 'r':
                    person["photo"] = value
                elif prefix == 'o':
                    notes_parts.append(value)
                    # Extract generation from notes
                    gen = self.extract_generation(value)
                    if gen:
                        person["generation"] = gen
                        person["generation_source"] = "explicit"
                    # Extract phai/chi
                    phai = self.extract_phai(value)
                    if phai:
                        person["phai"] = phai
                    chi = self.extract_chi(value)
                    if chi:
                        person["chi"] = chi
                elif prefix == 'A':
                    person["activities"] = value
                    # Also check for generation in activities
                    gen = self.extract_generation(value)
                    if gen and not person["generation"]:
                        person["generation"] = gen
                        person["generation_source"] = "explicit"
                elif prefix == 'v':
                    # Birth place
                    person["birth_place"] = value
                elif prefix == 'U':
                    # Burial place
                    person["burial_place"] = value
                elif prefix == 'F':
                    # Burial date (format: YYYYMMDD or 0000MMDD)
                    person["burial_date"] = self.parse_date(value)
                elif prefix == 'I':
                    # Interests
                    person["interests"] = value
                elif prefix == 'j':
                    # Profession/Occupation
                    person["profession"] = value
                elif prefix == 'E':
                    # Employer/Position
                    person["employer"] = value

            person["notes"] = " | ".join(notes_parts)
            self.persons[person_id] = person

        print(f"Đã đọc {len(self.persons)} người")

    def build_relationships(self):
        """Xây dựng các mối quan hệ gia đình"""
        print("Đang xây dựng mối quan hệ...")

        for pid, person in self.persons.items():
            # Build children index
            if person["father_id"] and person["father_id"] in self.persons:
                self.children_of[person["father_id"]].append(pid)
            if person["mother_id"] and person["mother_id"] in self.persons:
                self.children_of[person["mother_id"]].append(pid)

            # Build spouse index
            for spouse_id in person["spouse_ids"]:
                if spouse_id in self.persons:
                    self.spouse_of[pid].append(spouse_id)

        # Update children_ids in person records
        for parent_id, children in self.children_of.items():
            if parent_id in self.persons:
                self.persons[parent_id]["children_ids"] = list(set(children))

        # Build family units
        family_id = 1
        processed_couples = set()

        for pid, person in self.persons.items():
            if person["father_id"] and person["mother_id"]:
                couple_key = tuple(sorted([person["father_id"], person["mother_id"]]))
                if couple_key not in processed_couples:
                    processed_couples.add(couple_key)

                    # Find all children of this couple
                    children = []
                    for child_id, child in self.persons.items():
                        if (child["father_id"] == person["father_id"] and
                            child["mother_id"] == person["mother_id"]):
                            children.append(child_id)

                    self.families[f"F{family_id}"] = {
                        "id": f"F{family_id}",
                        "husband_id": person["father_id"] if self.persons.get(person["father_id"], {}).get("gender") == "male" else person["mother_id"],
                        "wife_id": person["mother_id"] if self.persons.get(person["mother_id"], {}).get("gender") == "female" else person["father_id"],
                        "children_ids": children
                    }
                    family_id += 1

        print(f"Đã xây dựng {len(self.families)} gia đình")

    def propagate_generations(self):
        """Suy luận thông tin đời từ liên kết cha-con"""
        print("Đang suy luận thông tin đời...")

        changes = True
        iterations = 0
        max_iterations = 20

        while changes and iterations < max_iterations:
            changes = False
            iterations += 1

            for pid, person in self.persons.items():
                if person["generation"] is not None:
                    continue

                # Từ cha
                if person["father_id"] and person["father_id"] in self.persons:
                    father = self.persons[person["father_id"]]
                    if father["generation"] is not None:
                        person["generation"] = father["generation"] + 1
                        person["generation_source"] = f"inferred_from_father:{father['id']}"
                        changes = True
                        continue

                # Từ mẹ (nếu họ Đặng)
                if person["mother_id"] and person["mother_id"] in self.persons:
                    mother = self.persons[person["mother_id"]]
                    if mother["generation"] is not None and "Đặng" in mother.get("surname", ""):
                        person["generation"] = mother["generation"] + 1
                        person["generation_source"] = f"inferred_from_mother:{mother['id']}"
                        changes = True
                        continue

                # Từ con
                for child_id in self.children_of.get(pid, []):
                    child = self.persons[child_id]
                    if child["generation"] is not None:
                        person["generation"] = child["generation"] - 1
                        person["generation_source"] = f"inferred_from_child:{child['id']}"
                        changes = True
                        break

        # Statistics
        explicit = sum(1 for p in self.persons.values() if p["generation_source"] == "explicit")
        inferred = sum(1 for p in self.persons.values() if p["generation_source"] and p["generation_source"].startswith("inferred"))
        unknown = sum(1 for p in self.persons.values() if p["generation"] is None)

        print(f"Hoàn thành sau {iterations} vòng lặp:")
        print(f"  - Rõ ràng: {explicit}")
        print(f"  - Suy luận: {inferred}")
        print(f"  - Không xác định: {unknown}")

    def compute_statistics(self) -> dict:
        """Tính toán các thống kê"""
        stats = {
            "total_members": len(self.persons),
            "total_families": len(self.families),
            "male_count": sum(1 for p in self.persons.values() if p["gender"] == "male"),
            "female_count": sum(1 for p in self.persons.values() if p["gender"] == "female"),
            "deceased_count": sum(1 for p in self.persons.values() if p["is_deceased"]),
            "alive_count": sum(1 for p in self.persons.values() if not p["is_deceased"]),
            "with_birth_date": sum(1 for p in self.persons.values() if p["birth_date"]),
            "with_birth_place": sum(1 for p in self.persons.values() if p["birth_place"]),
            "with_burial_place": sum(1 for p in self.persons.values() if p["burial_place"]),
            "with_profession": sum(1 for p in self.persons.values() if p["profession"]),
            "with_address": sum(1 for p in self.persons.values() if p["address"]),
            "with_email": sum(1 for p in self.persons.values() if p["email"]),
            "with_phone": sum(1 for p in self.persons.values() if p["phone"]),
            "generations": {},
            "phai_distribution": defaultdict(int),
            "chi_distribution": defaultdict(int),
        }

        # Generation distribution
        for person in self.persons.values():
            gen = person["generation"]
            if gen is not None:
                if gen not in stats["generations"]:
                    stats["generations"][gen] = {"count": 0, "male": 0, "female": 0}
                stats["generations"][gen]["count"] += 1
                if person["gender"] == "male":
                    stats["generations"][gen]["male"] += 1
                elif person["gender"] == "female":
                    stats["generations"][gen]["female"] += 1

            # Phai/Chi distribution
            if person["phai"]:
                stats["phai_distribution"][person["phai"]] += 1
            if person["chi"]:
                stats["chi_distribution"][person["chi"]] += 1

        stats["phai_distribution"] = dict(stats["phai_distribution"])
        stats["chi_distribution"] = dict(stats["chi_distribution"])
        stats["min_generation"] = min(stats["generations"].keys()) if stats["generations"] else None
        stats["max_generation"] = max(stats["generations"].keys()) if stats["generations"] else None

        return stats

    def build_tree_structure(self, root_id: str = "START", max_depth: int = None) -> Dict:
        """Xây dựng cấu trúc cây cho D3.js"""

        def build_node(person_id: str, depth: int = 0) -> Optional[Dict]:
            if person_id not in self.persons:
                return None

            if max_depth is not None and depth > max_depth:
                return None

            person = self.persons[person_id]
            node = {
                "id": person_id,
                "name": f"{person['surname']} {person['name']}".strip(),
                "generation": person["generation"],
                "gender": person["gender"],
                "is_deceased": person["is_deceased"],
                "phai": person["phai"],
                "children": []
            }

            # Add children
            for child_id in person.get("children_ids", []):
                child_node = build_node(child_id, depth + 1)
                if child_node:
                    node["children"].append(child_node)

            # Sort children by birth date or name
            def get_sort_key(child_node):
                person = self.persons.get(child_node["id"], {})
                birth = person.get("birth_date")
                year = birth.get("year", 9999) if birth else 9999
                return (year, child_node["name"])

            node["children"].sort(key=get_sort_key)

            return node

        return build_node(root_id)

    def export_json(self, output_file: str, include_tree: bool = True):
        """Export dữ liệu ra file JSON"""
        print(f"Đang xuất file JSON: {output_file}")

        # Find founder
        founder_id = "START"
        founder = self.persons.get(founder_id, {})

        output = {
            "metadata": {
                "family_name": "Tộc Đặng Non Nước",
                "founder_id": founder_id,
                "founder_name": f"{founder.get('surname', '')} {founder.get('name', '')}".strip(),
                "total_members": len(self.persons),
                "total_families": len(self.families),
                "total_generations": len(set(p["generation"] for p in self.persons.values() if p["generation"])),
                "generated_at": datetime.now().isoformat(),
                "source_file": str(self.input_file)
            },
            "statistics": self.compute_statistics(),
            "persons": self.persons,
            "families": self.families,
        }

        if include_tree:
            output["tree"] = self.build_tree_structure(founder_id, max_depth=5)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Đã xuất {len(self.persons)} người và {len(self.families)} gia đình")

        # Also export a minified version for web
        minified_file = output_file.replace('.json', '.min.json')
        with open(minified_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, separators=(',', ':'))
        print(f"Đã xuất file minified: {minified_file}")

    def export_tree_only(self, output_file: str, max_depth: int = 14):
        """Export chỉ cấu trúc cây cho D3.js"""
        print(f"Đang xuất cấu trúc cây: {output_file}")

        tree = self.build_tree_structure("START", max_depth=max_depth)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tree, f, ensure_ascii=False, indent=2)

        print(f"Đã xuất cấu trúc cây")

    def run(self, output_dir: str = None):
        """Chạy toàn bộ quá trình chuyển đổi"""
        if output_dir is None:
            output_dir = Path(self.input_file).parent

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Parse
        self.parse_familyscript()

        # Build relationships
        self.build_relationships()

        # Propagate generations
        self.propagate_generations()

        # Export full JSON
        self.export_json(str(output_dir / "family_data.json"))

        # Export tree structure only
        self.export_tree_only(str(output_dir / "family_tree.json"))

        # Print summary
        stats = self.compute_statistics()
        print("\n" + "=" * 60)
        print("TÓM TẮT")
        print("=" * 60)
        print(f"Tổng số người: {stats['total_members']}")
        print(f"Tổng số gia đình: {stats['total_families']}")
        print(f"Nam: {stats['male_count']} ({stats['male_count']*100/stats['total_members']:.1f}%)")
        print(f"Nữ: {stats['female_count']} ({stats['female_count']*100/stats['total_members']:.1f}%)")
        print(f"Còn sống: {stats['alive_count']}")
        print(f"Đã mất: {stats['deceased_count']}")
        print(f"Số đời: {stats['min_generation']} - {stats['max_generation']}")
        print("\nPhân bố theo đời:")
        for gen in sorted(stats['generations'].keys()):
            data = stats['generations'][gen]
            print(f"  Đời {gen}: {data['count']} người")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Chuyển đổi FamilyScript sang JSON')
    # Get script directory for relative paths
    script_dir = Path(__file__).parent.resolve()

    parser.add_argument('input', nargs='?',
                        default=str(script_dir / 'My-Family-20-Jan-2026-020424519.txt'),
                        help='File FamilyScript đầu vào')
    parser.add_argument('-o', '--output', default=str(script_dir / 'docs'),
                        help='Thư mục xuất (mặc định: docs folder)')

    args = parser.parse_args()

    converter = FamilyTreeConverter(args.input)
    converter.run(args.output)


if __name__ == "__main__":
    main()
