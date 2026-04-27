#!/usr/bin/env python3
"""
Bin Name Override Tool

Automates the process of checking .sbdefs against .bdefs and updating .py files
with correct bindefovrd entries to match the main bin definitions.

Usage:
    python bin_override_tool.py <py_file> <sbdefs_file> <bdefs_file> [--add-missing-bins]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, Set, Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class BinInfo:
    """Information about a bin definition."""
    bin_name: str
    bin_number: str
    description: str
    parent_bin_name: str
    
    @property
    def parent_bin_number(self) -> Optional[str]:
        """Extract parent bin number from parent bin name (e.g., b97_FAIL_... -> 97)."""
        match = re.match(r'b?(\d+)', self.parent_bin_name)
        return match.group(1) if match else None
    
    @property
    def is_hardbin(self) -> bool:
        """Check if this is a hardbin (2-3 digits) or softbin (4+ digits)."""
        return len(self.parent_bin_number) <= 3 if self.parent_bin_number else False


def parse_bin_definitions(file_path: Path) -> Dict[str, BinInfo]:
    """
    Parse a .bdefs or .sbdefs file and extract bin definitions.
    
    Returns:
        Dictionary mapping normalized bin numbers (without leading zeros) to BinInfo objects
    """
    bins = {}
    
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return bins
    
    content = file_path.read_text(encoding='utf-8')
    
    # Pattern matches: Bin <BinName> <BinNumber> : "<Description>", <ParentBinName>;
    # or: LeafBin <BinName> <BinNumber> : "<Description>", <ParentBinName>;
    pattern = r'(?:Leaf)?Bin\s+(\S+)\s+(\d+)\s*:\s*"([^"]+)"\s*,\s*(\S+)\s*;'
    
    for match in re.finditer(pattern, content):
        bin_name, bin_number, description, parent_bin_name = match.groups()
        # Normalize bin number by removing leading zeros
        normalized_bin_number = str(int(bin_number))
        bins[normalized_bin_number] = BinInfo(
            bin_name=bin_name,
            bin_number=bin_number,
            description=description,
            parent_bin_name=parent_bin_name
        )
    
    return bins


def find_bin_mismatches(sbdefs: Dict[str, BinInfo], bdefs: Dict[str, BinInfo]) -> Tuple[Dict[str, Tuple[str, str]], Set[str]]:
    """
    Compare sbdefs against bdefs to find mismatches.
    
    Returns:
        Tuple of:
        - Dictionary of mismatches: {bin_number: (sbdefs_parent, bdefs_parent)}
        - Set of parent bin numbers in sbdefs that don't exist in bdefs
    """
    mismatches = {}
    missing_parent_bins = set()
    
    # Get all unique parent bin numbers from sbdefs
    parent_bins_in_sbdefs = set()
    for bin_info in sbdefs.values():
        if bin_info.parent_bin_number:
            parent_bins_in_sbdefs.add(bin_info.parent_bin_number)
    
    # Check each parent bin number
    for parent_bin_num in parent_bins_in_sbdefs:
        # Normalize bin number by converting to int and back to string (removes leading zeros)
        normalized_bin_num = str(int(parent_bin_num))
        if normalized_bin_num not in bdefs:
            missing_parent_bins.add(parent_bin_num)
        else:
            # Check if the parent bin name matches
            sbdefs_parent_name = next(
                (b.parent_bin_name for b in sbdefs.values() 
                 if b.parent_bin_number == parent_bin_num),
                None
            )
            bdefs_parent_name = bdefs[normalized_bin_num].bin_name
            
            if sbdefs_parent_name and sbdefs_parent_name != bdefs_parent_name:
                mismatches[parent_bin_num] = (sbdefs_parent_name, bdefs_parent_name)
    
    return mismatches, missing_parent_bins


def format_bindefovrd_key(bin_number: str, is_hardbin: bool) -> str:
    """
    Format bin number for bindefovrd key (zero-padded).
    - Hardbins: 2 digits (e.g., "09", "97")
    - Softbins: 4 digits (e.g., "0900", "9700")
    """
    if is_hardbin:
        return bin_number.zfill(2)
    else:
        return bin_number.zfill(4)


def format_bindefovrd_value(bin_name: str, is_hardbin: bool) -> str:
    """
    Format bin name for bindefovrd value.
    - Hardbins: WITH 'b' prefix (e.g., "b09_FAIL_...")
    - Softbins: NO 'b' prefix (e.g., "0900_fail_...")
    """
    if is_hardbin:
        return bin_name if bin_name.startswith('b') else f'b{bin_name}'
    else:
        return bin_name.lstrip('b')


def generate_bindefovrd_entries(mismatches: Dict[str, Tuple[str, str]], bdefs: Dict[str, BinInfo]) -> Dict[str, str]:
    """
    Generate bindefovrd dictionary entries from mismatches.
    
    Returns:
        Dictionary with properly formatted bindefovrd entries
    """
    bindefovrd = {}
    
    for bin_number, (sbdefs_name, bdefs_name) in mismatches.items():
        # Normalize bin number by converting to int and back to string (removes leading zeros)
        normalized_bin_num = str(int(bin_number))
        # Determine if this is a hardbin (2-3 digits) or softbin (4+ digits) based on the bin number itself
        is_hardbin = len(bin_number) <= 3
        
        key = format_bindefovrd_key(bin_number, is_hardbin)
        value = format_bindefovrd_value(bdefs_name, is_hardbin)
        
        bindefovrd[key] = value
    
    return bindefovrd


def find_initialize_class(py_content: str) -> Optional[Tuple[str, int, int]]:
    """
    Find the Initialize class call in the .py file.
    
    Returns:
        Tuple of (class_name, start_pos, end_pos) or None if not found
    """
    # Match Initialize class patterns like:
    # InitializeCBRClass(...) or InitializeM5(...)
    pattern = r'(Initialize\w+)\s*\('
    
    match = re.search(pattern, py_content)
    if not match:
        return None
    
    class_name = match.group(1)
    start_pos = match.start()
    
    # Find the matching closing parenthesis
    depth = 0
    in_string = False
    string_char = None
    i = match.end()
    
    while i < len(py_content):
        char = py_content[i]
        
        # Handle string literals
        if char in ('"', "'") and (i == 0 or py_content[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        # Count parentheses when not in string
        if not in_string:
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    return (class_name, start_pos, i + 1)
                depth -= 1
        
        i += 1
    
    return None


def parse_existing_bindefovrd(init_call: str) -> Dict[str, str]:
    """
    Parse existing bindefovrd dictionary from Initialize class call.
    
    Returns:
        Dictionary of existing bindefovrd entries
    """
    existing_bindefovrd = {}
    
    # Find the bindefovrd parameter
    bindefovrd_pattern = r'bindefovrd\s*=\s*\{([^}]*)\}'
    match = re.search(bindefovrd_pattern, init_call, re.DOTALL)
    
    if not match:
        return existing_bindefovrd
    
    dict_content = match.group(1)
    
    # Parse key-value pairs: "key": "value"
    entry_pattern = r'["\']([^"\']*)["\'\s]*:\s*["\']([^"\']*)["\']'
    
    for entry_match in re.finditer(entry_pattern, dict_content):
        key, value = entry_match.groups()
        existing_bindefovrd[key] = value
    
    return existing_bindefovrd


def update_py_file_with_bindefovrd(py_file: Path, bindefovrd: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Update the .py file with bindefovrd entries.
    
    Returns:
        True if update was successful or would be successful (dry_run)
    """
    if not py_file.exists():
        print(f"Error: {py_file} does not exist")
        return False
    
    content = py_file.read_text(encoding='utf-8')
    
    # Find the Initialize class call
    init_info = find_initialize_class(content)
    if not init_info:
        print("Error: Could not find Initialize class in .py file")
        return False
    
    class_name, start_pos, end_pos = init_info
    init_call = content[start_pos:end_pos]
    
    # Check if bindefovrd already exists and parse existing entries
    bindefovrd_pattern = r'bindefovrd\s*=\s*\{[^}]*\}'
    existing_match = re.search(bindefovrd_pattern, init_call, re.DOTALL)
    
    # Parse existing bindefovrd entries
    existing_bindefovrd = parse_existing_bindefovrd(init_call) if existing_match else {}
    
    # Merge new entries with existing ones (new entries override existing for same keys)
    merged_bindefovrd = {**existing_bindefovrd, **bindefovrd}
    
    # Format the merged bindefovrd dictionary
    bindefovrd_lines = ["    bindefovrd={"]
    for key, value in sorted(merged_bindefovrd.items()):
        bindefovrd_lines.append(f'        "{key}": "{value}",')
    bindefovrd_lines.append("    }")
    bindefovrd_str = '\n'.join(bindefovrd_lines)
    
    if existing_match:
        # Replace existing bindefovrd
        new_init_call = init_call[:existing_match.start()] + bindefovrd_str + init_call[existing_match.end():]
    else:
        # Add bindefovrd before the closing parenthesis
        # Find the last parameter and add comma if needed
        last_param_end = init_call.rfind(',', 0, -1)
        if last_param_end == -1:
            # No parameters, add after opening parenthesis
            insert_pos = init_call.find('(') + 1
            new_init_call = init_call[:insert_pos] + '\n' + bindefovrd_str + '\n' + init_call[insert_pos:]
        else:
            # Find position before closing parenthesis
            close_paren = init_call.rfind(')')
            new_init_call = init_call[:close_paren] + ',\n' + bindefovrd_str + '\n' + init_call[close_paren:]
    
    new_content = content[:start_pos] + new_init_call + content[end_pos:]
    
    if dry_run:
        print("\n=== Would update .py file with: ===")
        if existing_bindefovrd:
            preserved = {k: v for k, v in existing_bindefovrd.items() if k not in bindefovrd}
            print(f"\nExisting entries that will be preserved: {len(preserved)}")
            print("\nEntries that will be added/updated:")
            for key, value in sorted(bindefovrd.items()):
                status = "updated" if key in existing_bindefovrd else "added"
                print(f'    "{key}": "{value}",  # {status}')
        print("\nFinal bindefovrd:")
        print(bindefovrd_str)
        return True
    else:
        py_file.write_text(new_content, encoding='utf-8')
        print(f"\n✓ Updated {py_file} with bindefovrd entries")
        if existing_bindefovrd:
            preserved = {k: v for k, v in existing_bindefovrd.items() if k not in bindefovrd}
            updated_count = sum(1 for k in bindefovrd.keys() if k in existing_bindefovrd)
            added_count = len(bindefovrd) - updated_count
            print(f"  - Preserved: {len(preserved)} existing entries")
            if updated_count > 0:
                print(f"  - Updated: {updated_count} entries")
            if added_count > 0:
                print(f"  - Added: {added_count} new entries")
        return True


def generate_missing_bin_entries(missing_bins: Set[str], bdefs: Dict[str, BinInfo], sbdefs: Dict[str, BinInfo], pad_softbin_names: bool = True) -> List[str]:
    """
    Generate .bdefs entries for missing parent bins.
    
    Args:
        pad_softbin_names: If True, generates names like b0900_FAIL. If False, b900_FAIL.
    
    Returns:
        List of formatted bin definition lines to add to .bdefs
    """
    entries = []
    
    for bin_number in sorted(missing_bins):
        # Find the parent bin name from sbdefs
        parent_name = next(
            (b.parent_bin_name for b in sbdefs.values() 
             if b.parent_bin_number == bin_number),
            None
        )
        
        if not parent_name:
            continue
        
        # Extract the parent hardbin number (first 2 digits of the softbin)
        match = re.match(r'b?(\d{2})', parent_name)
        if not match:
            continue
        
        parent_hardbin_num = match.group(1)
        
        # Find the parent hardbin in bdefs to get its naming convention
        # Normalize bin number by converting to int and back to string (removes leading zeros)
        normalized_hardbin_num = str(int(parent_hardbin_num))
        if normalized_hardbin_num in bdefs:
            parent_hardbin = bdefs[normalized_hardbin_num]
            # Generate softbin name from hardbin name
            # e.g., b09_FAIL_PIN_LEAKAGE -> b0900_FAIL_PIN_LEAKAGE or b900_FAIL_PIN_LEAKAGE
            bin_num_str = bin_number.zfill(4) if pad_softbin_names else bin_number
            softbin_name = f"b{bin_num_str}_{parent_hardbin.bin_name.split('_', 1)[1] if '_' in parent_hardbin.bin_name else parent_hardbin.bin_name.lstrip('b').lstrip(parent_hardbin_num).lstrip('_')}"
            description = softbin_name
            
            # Format: Bin <BinName> <BinNumber> : "<Description>", <ParentBinName>;
            # Normalize bin number to integer (remove leading zeros)
            normalized_bin_number = str(int(bin_number))
            entry = f'        Bin {softbin_name} {normalized_bin_number} : "{description}", {parent_hardbin.bin_name};'
            entries.append(entry)
    
    return entries


def insert_bins_into_bdefs(bdefs_file: Path, new_entries: List[str], dry_run: bool = False) -> bool:
    """
    Insert new bin entries into the .bdefs file in bin number order.
    
    Args:
        bdefs_file: Path to the .bdefs file
        new_entries: List of formatted bin entry strings to insert
        dry_run: If True, show what would be changed without modifying
    
    Returns:
        True if update was successful or would be successful (dry_run)
    """
    if not bdefs_file.exists():
        print(f"Error: {bdefs_file} does not exist")
        return False
    
    if not new_entries:
        return True
    
    content = bdefs_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Extract bin numbers from new entries
    new_bins_info = []
    for entry in new_entries:
        # Extract bin number from entry: "Bin <BinName> <BinNumber> :"
        match = re.search(r'Bin\s+\S+\s+(\d+)\s*:', entry)
        if match:
            bin_num = int(match.group(1))
            new_bins_info.append((bin_num, entry))
    
    if not new_bins_info:
        print("Error: Could not extract bin numbers from new entries")
        return False
    
    # Find all existing bin entries with their line numbers
    existing_bins = []
    for i, line in enumerate(lines):
        bin_match = re.search(r'^\s*Bin\s+\S+\s+(\d+)\s*:', line)
        if bin_match:
            bin_num = int(bin_match.group(1))
            existing_bins.append((bin_num, i))
    
    if not existing_bins:
        print("Error: Could not find any existing bin entries in .bdefs file")
        return False
    
    # For each new bin, find where to insert it
    insert_indices = []
    for new_bin_num, new_entry in new_bins_info:
        # Find the right position: after the last bin with a smaller number
        insert_line = None
        
        for existing_bin_num, line_num in existing_bins:
            if existing_bin_num < new_bin_num:
                # This bin is smaller, so we might insert after it
                insert_line = line_num + 1
            elif existing_bin_num > new_bin_num:
                # We've found a bin larger than ours, insert before it
                if insert_line is None:
                    insert_line = line_num
                break
        
        # If we didn't find a position, insert at the end of the last bin group
        if insert_line is None:
            # Find the last bin entry and insert after it
            if existing_bins:
                insert_line = existing_bins[-1][1] + 1
            else:
                print(f"Warning: Could not determine insertion point for bin {new_bin_num}")
                continue
        
        insert_indices.append((insert_line, new_entry, new_bin_num))
    
    if not insert_indices:
        print("Warning: Could not find appropriate location in .bdefs file")
        return False
    
    # Sort by line number in reverse to maintain correct positions during insertion
    insert_indices.sort(key=lambda x: x[0], reverse=True)
    
    # Insert entries
    for insert_pos, entry, bin_num in insert_indices:
        lines.insert(insert_pos, entry)
    
    new_content = '\n'.join(lines)
    
    if dry_run:
        print("\n=== Would add these entries to .bdefs: ===")
        for _, entry, bin_num in sorted(insert_indices, key=lambda x: x[2]):
            print(f"Bin {bin_num}: {entry}")
        return True
    else:
        bdefs_file.write_text(new_content, encoding='utf-8')
        print(f"✓ Added {len(insert_indices)} entries to {bdefs_file}")
        for _, _, bin_num in sorted(insert_indices, key=lambda x: x[2]):
            print(f"  - Added bin {bin_num}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Check .sbdefs against .bdefs and generate bindefovrd entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check and update .py file
  python bin_override_tool.py module.py module.sbdefs BinDefinitions.bdefs
  
  # Dry run (show what would be changed)
  python bin_override_tool.py module.py module.sbdefs BinDefinitions.bdefs --dry-run
        """
    )
    
    parser.add_argument('py_file', type=Path, help='Path to the .py module file')
    parser.add_argument('sbdefs_file', type=Path, help='Path to the .sbdefs file')
    parser.add_argument('bdefs_file', type=Path, help='Path to the .bdefs file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--no-pad-softbin-names', action='store_true', help='Generate softbin names without zero-padding (e.g., b900 instead of b0900)')
    
    args = parser.parse_args()
    
    # Parse the files
    print(f"Parsing {args.sbdefs_file}...")
    sbdefs = parse_bin_definitions(args.sbdefs_file)
    print(f"  Found {len(sbdefs)} bins in .sbdefs")
    
    print(f"\nParsing {args.bdefs_file}...")
    bdefs = parse_bin_definitions(args.bdefs_file)
    print(f"  Found {len(bdefs)} bins in .bdefs")
    
    # Find mismatches
    print("\nAnalyzing bin definitions...")
    mismatches, missing_bins = find_bin_mismatches(sbdefs, bdefs)
    
    # Report findings
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    
    if mismatches:
        print(f"\n✗ Found {len(mismatches)} parent bin name mismatches:")
        for bin_num, (sbdefs_name, bdefs_name) in sorted(mismatches.items()):
            print(f"  Bin {bin_num}:")
            print(f"    .sbdefs: {sbdefs_name}")
            print(f"    .bdefs:  {bdefs_name}")
    else:
        print("\n✓ No parent bin name mismatches found")
    
    if missing_bins:
        print(f"\n✗ Found {len(missing_bins)} parent bins in .sbdefs not present in .bdefs:")
        for bin_num in sorted(missing_bins):
            parent_name = next(
                (b.parent_bin_name for b in sbdefs.values() 
                 if b.parent_bin_number == bin_num),
                "Unknown"
            )
            print(f"  Bin {bin_num}: {parent_name}")
    else:
        print("\n✓ All parent bins exist in .bdefs")
    
    # Generate and apply bindefovrd entries
    if mismatches:
        print("\n" + "="*70)
        print("GENERATING BINDEFOVRD ENTRIES")
        print("="*70)
        
        bindefovrd = generate_bindefovrd_entries(mismatches, bdefs)
        
        print("\nGenerated bindefovrd entries:")
        print("bindefovrd = {")
        for key, value in sorted(bindefovrd.items()):
            print(f'    "{key}": "{value}",  # {"Hardbin" if len(key) <= 2 else "Softbin"}')
        print("}")
        
        # Update .py file
        print("\n" + "="*70)
        print("UPDATING .PY FILE")
        print("="*70)
        
        success = update_py_file_with_bindefovrd(args.py_file, bindefovrd, dry_run=args.dry_run)
        
        if success and not args.dry_run:
            print(f"\n✓ Successfully updated {args.py_file}")
            print("\nNext steps:")
            print("  1. Review the changes in the .py file")
            print("  2. Run pymtpl.py to regenerate .mtpl and .sbdefs")
            print("  3. Verify that parent bins now match")
        elif args.dry_run:
            print("\n(Dry run - no files were modified)")
    
    # Handle missing bins
    if missing_bins:
        print("\n" + "="*70)
        print("ADDING MISSING BIN ENTRIES TO .BDEFS")
        print("="*70)
        
        new_entries = generate_missing_bin_entries(missing_bins, bdefs, sbdefs, pad_softbin_names=not args.no_pad_softbin_names)
        
        if new_entries:
            if args.dry_run:
                print("\nWould add these entries to your .bdefs file:")
                print("\n".join(new_entries))
            else:
                success = insert_bins_into_bdefs(args.bdefs_file, new_entries, dry_run=args.dry_run)
                if success:
                    print("\nAdded entries:")
                    print("\n".join(new_entries))
                    print("\nNext steps:")
                    print("  1. Review the changes in the .bdefs file")
                    print("  2. Run this tool again to update bindefovrd with new bins")
                    print("  3. Run pymtpl.py to regenerate module files")
                else:
                    print("\n✗ Failed to update .bdefs file")
        else:
            print("\nCould not generate entries for missing bins")
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    has_issues = bool(mismatches or missing_bins)
    
    if not has_issues:
        print("\n✓ All bin definitions are consistent!")
        print("  No changes needed.")
        return 0
    
    # We found issues - check if we successfully fixed them
    if args.dry_run:
        # Dry run mode - show what would be changed
        if mismatches:
            print(f"\n→ Would update .py file with {len(mismatches)} bindefovrd entries")
        if missing_bins:
            print(f"\n→ Would add {len(missing_bins)} parent bins to .bdefs")
        return 1  # Exit with 1 in dry-run to indicate changes are needed
    else:
        # Real run mode - report what was done
        all_success = True
        
        if mismatches:
            print(f"\n✓ Updated .py file with {len(mismatches)} bindefovrd entries")
        
        if missing_bins:
            print(f"\n✓ Added {len(missing_bins)} parent bins to .bdefs")
            print("  Run this tool again to update bindefovrd with these new bins")
            # Exit with 1 to indicate user needs to run again
            return 1
        
        # All fixes applied successfully
        return 0


if __name__ == '__main__':
    sys.exit(main())
