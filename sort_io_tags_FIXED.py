#!/usr/bin/env python3
"""
Sort DB.csv by AccessName and ItemName for IODisc, IOInt, and IOReal groups.
Also outputs one CSV file per AccessName containing all tags for that AccessName,
with correct section headers, sorted by ItemName.

FIXED VERSION - Reads column headers to find correct column indices
"""
import sys
import os
import re

def read_file_with_encoding(filepath):
    """Try different encodings to read the file"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                lines = f.readlines()
                print(f"✓ Successfully read file with encoding: {encoding}")
                print(f"  Total lines: {len(lines)}")
                return lines, encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    raise Exception("Could not read file with any standard encoding")

def find_column_indices(header_line):
    """Parse header line to find AccessName and ItemName column indices"""
    parts = [p.strip() for p in header_line.strip().split(',')]
    
    accessname_idx = None
    itemname_idx = None
    
    print(f"\n  Parsing header columns:")
    for i, col in enumerate(parts):
        print(f"    Column {i}: '{col}'")
        if col.upper() == 'ACCESSNAME':
            accessname_idx = i
            print(f"      → Found AccessName at index {i}")
        elif col.upper() == 'ITEMNAME':
            itemname_idx = i
            print(f"      → Found ItemName at index {i}")
    
    return accessname_idx, itemname_idx

def get_accessname_from_row(data_line, accessname_idx):
    """Extract AccessName value from a data row, stripping surrounding quotes"""
    parts = data_line.strip().split(',')
    if accessname_idx < len(parts):
        return parts[accessname_idx].strip().strip('"')
    return None

def sanitize_filename(name):
    """Remove/replace characters that are invalid in filenames"""
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def sort_io_sections(input_file, output_file, per_access_dir):
    """
    Sort IODisc, IOInt, and IOReal sections by AccessName then ItemName.
    Also write one CSV per AccessName containing all its tags across all three
    IO section types, each section prefixed with its original header line.
    """
    
    print("=" * 80)
    print("CSV IO TAG SORTER - FIXED VERSION")
    print("Sort by AccessName then ItemName (using correct column headers)")
    print("Also outputs one CSV file per AccessName")
    print("=" * 80)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Per-AccessName dir: {per_access_dir}")
    print("=" * 80)
    print()
    
    # Read file
    lines, detected_encoding = read_file_with_encoding(input_file)
    
    result_lines = []
    current_section_name = None
    current_section_header_line = None
    current_section_data = []
    section_count = 0
    sorted_sections = []
    
    # Target sections to sort
    target_sections = [':IODisc', ':IOInt', ':IOReal']
    
    # Collect per-AccessName data:
    # { access_name: { section_name: (header_line, [data_lines]) } }
    per_access = {}
    
    print(f"\nTarget sections: {target_sections}\n")
    
    def process_section(section_name, section_header_line, section_data):
        """Sort a target section and collect rows into per_access dict."""
        nonlocal per_access

        accessname_idx, itemname_idx = find_column_indices(section_name)
        
        if accessname_idx is None or itemname_idx is None:
            print(f"\n  ⚠ WARNING: Could not find AccessName or ItemName columns!")
            print(f"    AccessName index: {accessname_idx}")
            print(f"    ItemName index: {itemname_idx}")
            print(f"    Skipping sort for this section.")
            return section_data
        
        print(f"\n  Using columns:")
        print(f"    AccessName = column {accessname_idx}")
        print(f"    ItemName = column {itemname_idx}")
        
        # Show first few rows BEFORE sorting
        print(f"\n  First 3 rows BEFORE sorting:")
        for i, row in enumerate(section_data[:3]):
            parts = row.strip().split(',')
            access = parts[accessname_idx] if accessname_idx < len(parts) else "?"
            item = parts[itemname_idx] if itemname_idx < len(parts) else "?"
            print(f"    {i+1}. AccessName='{access}', ItemName='{item}'")
        
        # Sort the data
        def sort_key(data_line):
            parts = data_line.strip().split(',')
            access_name = parts[accessname_idx].strip().lower() if accessname_idx < len(parts) else ""
            item_name = parts[itemname_idx].strip().lower() if itemname_idx < len(parts) else ""
            return (access_name, item_name)
        
        sorted_data = sorted(section_data, key=sort_key)
        
        # Show first few rows AFTER sorting
        print(f"\n  First 3 rows AFTER sorting:")
        for i, row in enumerate(sorted_data[:3]):
            parts = row.strip().split(',')
            access = parts[accessname_idx] if accessname_idx < len(parts) else "?"
            item = parts[itemname_idx] if itemname_idx < len(parts) else "?"
            print(f"    {i+1}. AccessName='{access}', ItemName='{item}'")
        
        order_changed = sorted_data != section_data
        print(f"\n  Order changed? {order_changed}")
        if order_changed:
            print(f"  ✓ Data was re-sorted!")
        else:
            print(f"  → Data was already in correct order")
        
        # Collect rows into per_access dict (sorted by ItemName within each AccessName)
        for row in sorted_data:
            access_name = get_accessname_from_row(row, accessname_idx)
            if access_name:
                if access_name not in per_access:
                    per_access[access_name] = {}
                bare_section = section_name.split(',')[0]
                if bare_section not in per_access[access_name]:
                    per_access[access_name][bare_section] = (section_header_line, [])
                per_access[access_name][bare_section][1].append(row)
        
        return sorted_data
    
    # ------------------------------------------------------------------ #
    # Main parse loop
    # ------------------------------------------------------------------ #
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for section header (starts with ':')
        if stripped.startswith(':'):
            # Process previous section if it was a target
            if current_section_data and current_section_name:
                bare_name = current_section_name.split(',')[0]
                should_sort = any(bare_name == target for target in target_sections)
                
                if should_sort:
                    print(f"\n{'='*80}")
                    print(f"Processing target section: {bare_name}")
                    print(f"  Line: {line_num - len(current_section_data) - 1}")
                    print(f"  Data rows: {len(current_section_data)}")
                    
                    sorted_data = process_section(
                        current_section_name,
                        current_section_header_line,
                        current_section_data
                    )
                    result_lines.extend(sorted_data)
                    sorted_sections.append(bare_name)
                else:
                    result_lines.extend(current_section_data)
            
            # Add new section header
            result_lines.append(line)
            current_section_name = stripped
            current_section_header_line = line
            current_section_data = []
            section_count += 1
            
        elif current_section_name and stripped:
            current_section_data.append(line)
        
        elif not stripped:
            if not current_section_data:
                result_lines.append(line)
        
        else:
            if current_section_name is None:
                result_lines.append(line)
    
    # Process last section
    if current_section_data and current_section_name:
        bare_name = current_section_name.split(',')[0]
        should_sort = any(bare_name == target for target in target_sections)
        
        if should_sort:
            print(f"\n{'='*80}")
            print(f"Processing LAST target section: {bare_name}")
            print(f"  Data rows: {len(current_section_data)}")
            
            sorted_data = process_section(
                current_section_name,
                current_section_header_line,
                current_section_data
            )
            result_lines.extend(sorted_data)
            sorted_sections.append(bare_name)
        else:
            result_lines.extend(current_section_data)
    
    # ------------------------------------------------------------------ #
    # Write main sorted output
    # ------------------------------------------------------------------ #
    with open(output_file, 'w', encoding=detected_encoding, newline='') as f:
        f.writelines(result_lines)
    
    # ------------------------------------------------------------------ #
    # Write per-AccessName CSV files
    # ------------------------------------------------------------------ #
    os.makedirs(per_access_dir, exist_ok=True)
    
    # Section order for output files (consistent ordering)
    section_order = [':IODisc', ':IOInt', ':IOReal']
    
    print(f"\n{'='*80}")
    print(f"Writing per-AccessName CSV files to: {per_access_dir}")
    print(f"{'='*80}")
    
    files_written = []
    for access_name in sorted(per_access.keys(), key=str.lower):
        safe_name = sanitize_filename(access_name)
        out_path = os.path.join(per_access_dir, f"{safe_name}.csv")
        
        rows_written = 0
        with open(out_path, 'w', encoding=detected_encoding, newline='') as f:
            for section_key in section_order:
                if section_key in per_access[access_name]:
                    header_line, data_rows = per_access[access_name][section_key]
                    f.write(header_line)          # e.g. ":IODisc,Group,Comment,..."
                    for row in data_rows:
                        f.write(row)
                    rows_written += len(data_rows)
        
        print(f"  ✓ {safe_name}.csv  ({rows_written} tags)")
        files_written.append(out_path)
    
    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"✓ Total sections found: {section_count}")
    print(f"✓ Target sections sorted: {len(sorted_sections)}")
    if sorted_sections:
        for section in sorted_sections:
            print(f"    - {section}")
    else:
        print(f"  ⚠ No target sections were found or sorted!")
    print(f"✓ Output written to: {output_file}")
    print(f"✓ Total lines written: {len(result_lines)}")
    print(f"✓ Per-AccessName files written: {len(files_written)}")
    for fp in files_written:
        print(f"    - {os.path.basename(fp)}")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file  = os.path.join(script_dir, 'DB.csv')
    output_file = os.path.join(script_dir, 'DB_IOSorted.csv')
    per_access_dir = os.path.join(script_dir, 'ByAccessName')
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        success = sort_io_sections(input_file, output_file, per_access_dir)
        if success:
            print("\n✓ Success!")
            print(f"  Main sorted file : DB_IOSorted.csv")
            print(f"  Per-AccessName   : ByAccessName\\<AccessName>.csv")
            input("\nPress Enter to exit...")
            sys.exit(0)
        else:
            print("\nERROR: Sorting failed")
            input("\nPress Enter to exit...")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
