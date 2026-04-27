#!/usr/bin/env python3
"""
Create a new Pymtpl module with all required files and directory structure.

This script automates most of the module creation workflow
"""

import argparse
import json
import os
import sys
from pathlib import Path
import shutil
import re


def create_directory_structure(module_path: Path) -> None:
    """Create module directory and InputFiles subdirectory."""
    module_path.mkdir(parents=True, exist_ok=True)
    input_files_path = module_path / "InputFiles"
    input_files_path.mkdir(exist_ok=True)
    print(f"✓ Created directory structure: {module_path}")


def create_mtproj_file(module_path: Path, module_name: str) -> None:
    """Create .mtproj file with proper XML structure."""
    mtproj_content = f"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup Label="Globals">
    <CustomProjectExtensionsPath Condition=" '$(CustomProjectExtensionsPath)' == '' ">$(TorchCustomProjectPath)\\</CustomProjectExtensionsPath>
  </PropertyGroup>
  <Import Project="$(CustomProjectExtensionsPath)Torch.ProjectSystem.Module.props" />
  <ItemGroup>
    <Folder Include="InputFiles\\" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\..\\Shared\\Common\\Common.ctproj" />
  </ItemGroup>
  <Import Project="$(CustomProjectExtensionsPath)Torch.ProjectSystem.Module.targets" />
</Project>
"""
    mtproj_path = module_path / f"{module_name}.mtproj"
    mtproj_path.write_text(mtproj_content, encoding='utf-8')
    print(f"✓ Created {mtproj_path.name}")


def create_mconfig_file(module_path: Path, module_name: str) -> None:
    """Create .mconfig file with initial p0 patch."""
    mconfig_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="\\\\amr\\ec\\proj\\mdl\\sc\\intel\\hdmxpats\\PRODUCT\\{module_name}" Rev="RevTC0.0" Patch="p0" >
            <PlistFiles>
                <PlistFile>{module_name}.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
"""
    mconfig_path = module_path / f".mconfig"
    mconfig_path.write_text(mconfig_content, encoding='utf-8')
    print(f"✓ Created {mconfig_path.name}")


def create_binlimits_file(module_path: Path, module_name: str) -> None:
    """Create .BinLimits.json file with placeholder values."""
    binlimits_data = {
        "BinLimits": [[9800, 9899], [9900, 9999]],
        "Comment": "Placeholder bin limits - update with actual ranges",
        "Comment2": "Any field other than BinLimits is ignored"
    }
    binlimits_path = module_path / f"{module_name}.BinLimits.json"
    with open(binlimits_path, 'w', encoding='utf-8') as f:
        json.dump(binlimits_data, f, indent=2)
    print(f"✓ Created {binlimits_path.name}")


def create_tpmodule_file(module_path: Path, module_name: str) -> None:
    """Create .tpmodule file with module name."""
    tpmodule_path = module_path / f".tpmodule"
    tpmodule_path.write_text(module_name, encoding='utf-8')
    print(f"✓ Created {tpmodule_path.name}")


def create_python_file(module_path: Path, module_name: str, template_path: Path, initialize_class: str) -> None:
    """Create .py file from template with MODULE_NAME and Initialize class substitution."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    template_content = template_path.read_text(encoding='utf-8')
    
    # Replace MODULE_NAME variable assignment
    updated_content = re.sub(
        r'MODULE_NAME\s*=\s*["\'][^"\']+["\']',
        f'MODULE_NAME = "{module_name}"',
        template_content
    )
    
    # Replace InitializeXYZ with actual Initialize class name (multiline aware)
    # First, replace in the import statement
    updated_content = re.sub(
        r'from pymtpl\.core import (.*)InitializeXYZ',
        lambda m: f"from pymtpl.core import {m.group(1)}{initialize_class}",
        updated_content
    )
    
    # Replace InitializeXYZ function call (handles multiline)
    updated_content = re.sub(
        r'InitializeXYZ\s*\(',
        f'{initialize_class}(',
        updated_content,
        flags=re.MULTILINE
    )
    
    # Replace in comments
    updated_content = re.sub(
        r'# InitializeXYZ',
        f'# {initialize_class}',
        updated_content
    )
    
    py_path = module_path / f"{module_name}.py"
    py_path.write_text(updated_content, encoding='utf-8')
    print(f"✓ Created {py_path.name}")


def get_mtproj_type_guid(sln_content: str) -> str:
    """
    Extract the project type GUID used for .mtproj files from existing solution.
    
    Looks for existing .mtproj references in the .sln file and extracts their type GUID.
    Falls back to a common GUID if none found.
    """
    # Search for existing .mtproj project entries
    # Pattern: Project("{GUID}") = "name", "path.mtproj", "{instance-guid}"
    import re
    pattern = r'Project\("\{([A-F0-9-]+)\}"\)\s*=\s*"[^"]+",\s*"[^"]*\.mtproj"'
    matches = re.findall(pattern, sln_content, re.IGNORECASE)
    
    if matches:
        # Use the GUID from the first .mtproj project found
        return matches[0]
    
    # Fallback: Common Visual Studio project type GUIDs
    # Note: This may need to be customized per test program
    # FAE04EC0-301F-11D3-BF4B-00C04F79EFBC = C# project (common fallback)
    print("⚠ Warning: Could not detect .mtproj project type GUID from existing projects.")
    print("   Using default GUID. Verify in Visual Studio if solution doesn't load correctly.")
    return "FAE04EC0-301F-11D3-BF4B-00C04F79EFBC"


def update_sln_file(sln_path: Path, module_name: str, mtproj_rel_path: str, project_type_guid: str = None) -> None:
    """Add module project reference to .sln file with full configuration sections."""
    if not sln_path.exists():
        print(f"⚠ Warning: .sln file not found: {sln_path}")
        return
    
    content = sln_path.read_text(encoding='utf-8')
    
    # Auto-detect project type GUID if not provided
    if not project_type_guid:
        project_type_guid = get_mtproj_type_guid(content)
    
    # Generate unique instance GUID for this project (simple hash-based approach)
    import hashlib
    guid = hashlib.md5(module_name.encode()).hexdigest()
    formatted_guid = f"{guid[:8]}-{guid[8:12]}-{guid[12:16]}-{guid[16:20]}-{guid[20:32]}".upper()
    
    # Create project entry with detected or provided project type GUID
    project_entry = f'Project("{{{project_type_guid}}}") = "{module_name}", "{mtproj_rel_path}", "{{{formatted_guid}}}"\nEndProject\n'
    
    # Find insertion point (before Global)
    if 'Global' in content:
        content = content.replace('Global', project_entry + 'Global', 1)
    else:
        print(f"⚠ Warning: Could not find insertion point in {sln_path.name}")
        return
    
    # Add ProjectConfigurationPlatforms entries
    config_entries = f"\t\t{{{formatted_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU\n"
    config_entries += f"\t\t{{{formatted_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU\n"
    config_entries += f"\t\t{{{formatted_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU\n"
    config_entries += f"\t\t{{{formatted_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU\n"
    
    # Find ProjectConfigurationPlatforms section
    config_section_match = re.search(r'(GlobalSection\(ProjectConfigurationPlatforms\) = postSolution\n)', content)
    if config_section_match:
        insertion_point = config_section_match.end()
        content = content[:insertion_point] + config_entries + content[insertion_point:]
    else:
        print(f"⚠ Warning: Could not find ProjectConfigurationPlatforms section")
    
    # Add NestedProjects entry (under Modules folder)
    # Find the Modules folder GUID
    modules_guid_match = re.search(r'Project\("\{[A-F0-9-]+\}"\) = "Modules", "Modules", "\{([A-F0-9-]+)\}"', content)
    if modules_guid_match:
        modules_guid = modules_guid_match.group(1)
        nested_entry = f"\t\t{{{formatted_guid}}} = {{{modules_guid}}}\n"
        
        # Find NestedProjects section
        nested_section_match = re.search(r'(GlobalSection\(NestedProjects\) = preSolution\n)', content)
        if nested_section_match:
            insertion_point = nested_section_match.end()
            content = content[:insertion_point] + nested_entry + content[insertion_point:]
        else:
            print(f"⚠ Warning: Could not find NestedProjects section")
    else:
        print(f"⚠ Warning: Could not find Modules folder GUID")
    
    sln_path.write_text(content, encoding='utf-8')
    print(f"✓ Updated {sln_path.name} (project GUID: {formatted_guid})")


def update_file_reference(file_path: Path, reference_file: str, search_pattern: str = None) -> None:
    """Add reference to .imp, .stpl, or .tpproj file."""
    if not file_path.exists():
        print(f"⚠ Warning: File not found: {file_path}")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # Ensure proper path format with ..\..\
    if not reference_file.startswith('..\\'):
        reference_file = f'..\\..\\{reference_file}'
    
    # Check if reference already exists
    if reference_file in content:
        print(f"⚠ Reference already exists in {file_path.name}")
        return
    
    # For .tpproj (XML format)
    if file_path.suffix == '.tpproj':
        
        formatted_ref = f'    <ProjectReference Include="{reference_file}" />'
        
        # Find where to insert alphabetically within ProjectReference ItemGroup
        lines = content.split('\n')
        insertion_index = -1
        in_project_ref_section = False
        
        for i, line in enumerate(lines):
            if '<ProjectReference Include=' in line and '..\\..\\Modules\\' in line:
                in_project_ref_section = True
                # Extract module name from existing line for comparison
                existing_match = re.search(r'\\Modules\\([^\\]+)\\', line)
                new_match = re.search(r'\\Modules\\([^\\]+)\\', formatted_ref)
                if existing_match and new_match:
                    if new_match.group(1) > existing_match.group(1):
                        # Keep searching for correct position
                        insertion_index = i + 1
                    elif insertion_index == -1:
                        # Found first entry that comes after new entry
                        insertion_index = i
                        break
            elif in_project_ref_section and '<ProjectReference Include=' in line and '..\\..\\Shared\\' in line:
                # Found the Shared\Common reference, insert before it
                if insertion_index == -1:
                    insertion_index = i
                break
        
        if insertion_index >= 0:
            lines.insert(insertion_index, formatted_ref)
            content = '\n'.join(lines)
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ Updated {file_path.name} (inserted alphabetically)")
        else:
            print(f"⚠ Warning: Could not find insertion point in {file_path.name}")
        return
    
    # For .stpl (SubTestPlan format)
    if file_path.suffix == '.stpl':
        # Convert backslashes to forward slashes and wrap in quotes
        formatted_ref = reference_file.replace('\\', '/')
        # Add ../../ prefix and quotes/semicolon
        formatted_ref = f'\t"../../{formatted_ref}";'
        
        # Find the Final line to insert before it
        lines = content.split('\n')
        insertion_index = -1
        
        for i, line in enumerate(lines):
            if 'Final' in line:
                # Found the Final line, now find where to insert alphabetically
                # Search backwards from Final line to find correct position
                for j in range(i - 1, -1, -1):
                    if lines[j].strip().startswith('"../../Modules/'):
                        # Extract module name from existing line for comparison
                        existing_match = re.search(r'"../../Modules/([^/]+)/', lines[j])
                        new_match = re.search(r'"../../Modules/([^/]+)/', formatted_ref)
                        if existing_match and new_match:
                            if new_match.group(1) > existing_match.group(1):
                                # Insert after this line
                                insertion_index = j + 1
                                break
                    elif lines[j].strip() == '{':
                        # Reached the opening brace, insert after it
                        insertion_index = j + 1
                        break
                break
        
        if insertion_index >= 0:
            lines.insert(insertion_index, formatted_ref)
            content = '\n'.join(lines)
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ Updated {file_path.name} (inserted alphabetically)")
        else:
            print(f"⚠ Warning: Could not find insertion point in {file_path.name}")
        return
    
    # For .imp (Import format)
    if file_path.suffix == '.imp':
        # Convert backslashes to forward slashes
        formatted_ref = reference_file.replace('\\', '/')
        # Add Import prefix, ../../ prefix, and quotes/semicolon
        formatted_ref = f'Import "../../{formatted_ref}";'
        
        # Find where to insert alphabetically
        lines = content.split('\n')
        insertion_index = -1
        
        # Search for existing Import statements
        for i, line in enumerate(lines):
            if line.strip().startswith('Import "../../Modules/'):
                # Extract module name from existing line for comparison
                existing_match = re.search(r'Import "../../Modules/([^/]+)/', line)
                new_match = re.search(r'Import "../../Modules/([^/]+)/', formatted_ref)
                if existing_match and new_match:
                    if new_match.group(1) > existing_match.group(1):
                        # Keep searching for correct position
                        insertion_index = i + 1
                    elif insertion_index == -1:
                        # Found first entry that comes after new entry
                        insertion_index = i
                        break
        
        # If we went through all Import statements, insert at the end
        if insertion_index >= 0:
            lines.insert(insertion_index, formatted_ref)
            content = '\n'.join(lines)
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ Updated {file_path.name} (inserted alphabetically)")
        else:
            print(f"⚠ Warning: Could not find insertion point in {file_path.name}")
        return
    
    # For .tpproj and other simple text files
    # Add at the end of file
    if not content.endswith('\n'):
        content += '\n'
    content += f"{reference_file}\n"
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Updated {file_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Create a new Pymtpl module with all required files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create module with full solution integration
  python create_module.py PTH_NEW --initialize InitializeMTL --imp TestProgram/TestProgram.imp --stpl TestProgram/TestProgram.stpl --tpproj TestProgram/TestProgram.tpproj
        """
    )
    
    parser.add_argument('module_name', help='Name of the module to create (e.g., PTH_DTS)')
    parser.add_argument('--initialize', required=True, help='Initialize class name (e.g., InitializeMTL, InitializeLNL)')
    parser.add_argument('--workspace-root', default='.', help='Workspace root directory (default: current directory)')
    parser.add_argument('--template', help='Path to module_template.py (default: auto-detect)')
    parser.add_argument('--imp', required=True, help='Path to .imp file for solution integration')
    parser.add_argument('--stpl', required=True, help='Path to .stpl file for solution integration')
    parser.add_argument('--tpproj', required=True, help='Path to .tpproj file for solution integration')
    parser.add_argument('--sln', help='Path to .sln file (default: auto-detect in workspace root)')
    parser.add_argument('--project-type-guid', help='Project type GUID for .sln (default: auto-detect from existing .mtproj projects)')
    
    args = parser.parse_args()
    
    # Setup paths
    workspace_root = Path(args.workspace_root).resolve()
    module_path = workspace_root / "Modules" / args.module_name
    
    # Check if module already exists
    if module_path.exists():
        print(f"✗ Error: Module already exists: {module_path}")
        print(f"  Choose a different name or delete the existing module first.")
        sys.exit(1)
    
    # Find template file
    if args.template:
        template_path = Path(args.template)
    else:
        # Auto-detect template
        template_path = workspace_root / ".github" / "instructions" / "pymtpl" / "templates" / "module_template.py"
        if not template_path.exists():
            # Try alternative location
            script_dir = Path(__file__).parent
            template_path = script_dir / ".." / ".." / "instructions" / "pymtpl" / "templates" / "module_template.py"
    
    if not template_path.exists():
        print(f"✗ Error: Template file not found: {template_path}")
        print(f"  Use --template to specify the path to module_template.py")
        sys.exit(1)
    
    print(f"\nCreating module: {args.module_name}")
    print(f"Workspace root: {workspace_root}")
    print(f"Template: {template_path}\n")
    
    try:
        # Phase 1: Create directory and configuration files (Steps 2-7)
        print("Phase 1: Creating directory structure and configuration files...")
        create_directory_structure(module_path)
        create_mtproj_file(module_path, args.module_name)
        create_mconfig_file(module_path, args.module_name)
        create_binlimits_file(module_path, args.module_name)
        create_tpmodule_file(module_path, args.module_name)
        
        # Phase 2: Create Python file (Step 8)
        print("\nPhase 2: Creating Python module file...")
        create_python_file(module_path, args.module_name, template_path, args.initialize)
        
        print(f"\n✓ Module files created successfully in {module_path}")
        
        # Phase 3: Solution integration (Steps 10-13)
        print(f"\nPhase 3: Updating solution files...")
        
        # Compute relative path for .mtproj
        mtproj_rel_path = f"Modules\\{args.module_name}\\{args.module_name}.mtproj"
        
        # Update .sln
        if args.sln:
            sln_path = Path(args.sln)
            update_sln_file(sln_path, args.module_name, mtproj_rel_path, args.project_type_guid)
        else:
            # Auto-detect .sln in workspace root
            sln_files = list(workspace_root.glob("*.sln"))
            if len(sln_files) == 1:
                update_sln_file(sln_files[0], args.module_name, mtproj_rel_path, args.project_type_guid)
            elif len(sln_files) > 1:
                print(f"⚠ Warning: Multiple .sln files found. Use --sln to specify which one.")
        
        # Update .imp
        imp_path = Path(args.imp) if Path(args.imp).is_absolute() else workspace_root / args.imp
        sbdefs_ref = f"Modules\\{args.module_name}\\{args.module_name}.sbdefs"
        update_file_reference(imp_path, sbdefs_ref)
        
        # Update .stpl
        stpl_path = Path(args.stpl) if Path(args.stpl).is_absolute() else workspace_root / args.stpl
        mtpl_ref = f"Modules\\{args.module_name}\\{args.module_name}.mtpl"
        update_file_reference(stpl_path, mtpl_ref)
        
        # Update .tpproj
        tpproj_path = Path(args.tpproj) if Path(args.tpproj).is_absolute() else workspace_root / args.tpproj
        update_file_reference(tpproj_path, mtproj_rel_path)
        
        print(f"\n✓ Solution integration completed")
        print(f"\nNext steps:")
        print(f"  1. Run pymtpl.py to compile the module (see pymtpl-compiler skill)")
        print(f"  2. Add test content using add-test-content skill if needed")
        
        print(f"\n✓ Module creation complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
