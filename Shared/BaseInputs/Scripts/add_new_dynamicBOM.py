import xml.etree.ElementTree as ET
import os
import glob
import re

MSBUILD_NS = 'http://schemas.microsoft.com/developer/msbuild/2003'
ET.register_namespace('', MSBUILD_NS)

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    elif not elem.tail or not elem.tail.strip():
        elem.tail = "\n"

def fix_project_tag_order_and_xml_decl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Fix XML declaration to use double quotes
    if lines and lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="utf-8"?>\n'
    # Fix <Project ...> tag attribute order
    for i, line in enumerate(lines):
        if line.strip().startswith('<Project '):
            attrs = dict(re.findall(r'(\w+)="([^"]+)"', line))
            new_tag = f'<Project ToolsVersion="{attrs.get("ToolsVersion", "")}" DefaultTargets="{attrs.get("DefaultTargets", "")}" xmlns="{attrs.get("xmlns", MSBUILD_NS)}">'
            lines[i] = new_tag + '\n'
            break
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def should_add_itemgroup(file_path):
    filename = os.path.basename(file_path)
    is_mtproj = filename.lower().endswith('.mtproj')
    in_modules = 'modules' in file_path.replace('\\', '/').lower()
    if is_mtproj and in_modules:
        return True
    is_files_tproj = re.search(r'[^\\/]+_Files\.[^\\/]*tproj$', filename, re.IGNORECASE)
    is_common_files = filename.lower() == 'common_files.ctproj'
    if is_files_tproj and not is_common_files:
        return True
    return False

def get_folder_two_levels_up(file_path):
    folder = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
    return folder

def get_project_reference_pattern(root, ns):
    for item_group in root.findall('msbuild:ItemGroup', ns):
        for pr in item_group.findall('msbuild:ProjectReference', ns):
            include = pr.get('Include')
            match = re.match(r'(.*\\BaseInputs\\[^\\]+\\)([^\\]+_)(Class_.*)\\([^\\]+)\.(\w+proj)$', include)
            if match:
                prefix = match.group(1)      # e.g., '..\..\..\BaseInputs\GCD\'
                base_prefix = match.group(2) # e.g., 'GCD_'
                ext = match.group(5)         # e.g., 'ipctproj' or 'ctproj'
                return prefix, base_prefix, ext
    return None, None, 'ipctproj'

def update_common_project_reference(root, ns, filename):
    # Only for ipctproj files not starting with Common_
    if filename.endswith('.ipctproj') and not filename.startswith('Common_'):
        match = re.match(r'[^_]+_(Class_.*)\.ipctproj$', filename)
        if match:
            bom_name_from_file = match.group(1)
            correct_include = f"..\\..\\..\\Shared\\BaseInputs\\Common\\Common_{bom_name_from_file}\\Common_{bom_name_from_file}.ctproj"
            # Find all ProjectReference to Common
            to_remove = []
            found_correct = False
            for item_group in root.findall('msbuild:ItemGroup', ns):
                for pr in list(item_group.findall('msbuild:ProjectReference', ns)):
                    include = pr.get('Include')
                    if r'BaseInputs\Common\Common_' in include:
                        if include == correct_include:
                            found_correct = True
                        else:
                            to_remove.append((item_group, pr))
            # Remove all incorrect ProjectReferences to Common
            for item_group, pr in to_remove:
                item_group.remove(pr)
            # If not found, add after last <Import>
            if not found_correct:
                # Find the last <Import> element
                imports = root.findall('msbuild:Import', ns)
                if imports:
                    last_import = imports[-1]
                    parent = root
                    idx = list(parent).index(last_import)
                    # Insert new ItemGroup after last Import
                    new_itemgroup = ET.Element(f'{{{MSBUILD_NS}}}ItemGroup')
                    new_pr = ET.SubElement(new_itemgroup, f'{{{MSBUILD_NS}}}ProjectReference')
                    new_pr.set('Include', correct_include)
                    parent.insert(idx + 1, new_itemgroup)
                else:
                    # Fallback: append to root
                    new_itemgroup = ET.Element(f'{{{MSBUILD_NS}}}ItemGroup')
                    new_pr = ET.SubElement(new_itemgroup, f'{{{MSBUILD_NS}}}ProjectReference')
                    new_pr.set('Include', correct_include)
                    root.append(new_itemgroup)

def has_project_configuration(file_path):
    """Check if the file contains a <ProjectConfiguration> element."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'msbuild': MSBUILD_NS}
        for item_group in root.findall('msbuild:ItemGroup', ns):
            if item_group.get('Label') == 'ProjectConfigurations':
                if item_group.find('msbuild:ProjectConfiguration', ns) is not None:
                    return True
        return False
    except Exception:
        return False

def add_bom_to_tproj(file_path, bom_name):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'msbuild': MSBUILD_NS}

    # Always add ProjectConfiguration for BOM if not present
    for item_group in root.findall('msbuild:ItemGroup', ns):
        if item_group.get('Label') == 'ProjectConfigurations':
            exists = any(
                pc.get('Include') == f"{bom_name}|AnyCPU"
                for pc in item_group.findall('msbuild:ProjectConfiguration', ns)
            )
            if not exists:
                pc = ET.Element(f'{{{MSBUILD_NS}}}ProjectConfiguration', Include=f"{bom_name}|AnyCPU")
                conf = ET.SubElement(pc, f'{{{MSBUILD_NS}}}Configuration')
                conf.text = bom_name
                plat = ET.SubElement(pc, f'{{{MSBUILD_NS}}}Platform')
                plat.text = 'AnyCPU'
                item_group.append(pc)
            break

    # Update Common ProjectReference for ipctproj files not starting with Common_
    filename = os.path.basename(file_path)
    update_common_project_reference(root, ns, filename)

    if should_add_itemgroup(file_path):
        config_names = []
        for item_group in root.findall('msbuild:ItemGroup', ns):
            if item_group.get('Label') == 'ProjectConfigurations':
                for pc in item_group.findall('msbuild:ProjectConfiguration', ns):
                    conf = pc.find('msbuild:Configuration', ns)
                    if conf is not None and conf.text and conf.text not in ('Debug', 'Release'):
                        config_names.append(conf.text)
                break
        if bom_name not in config_names:
            config_names.append(bom_name)

        folder_two_up = get_folder_two_levels_up(file_path)
        prefix, base_prefix, ext = get_project_reference_pattern(root, ns)
        if not prefix:
            input_folder = folder_two_up
            prefix = f"..\\..\\..\\BaseInputs\\{input_folder}\\"
            base_prefix = f"{input_folder}_"
            ext = 'ipctproj'

        for conf in config_names:
            found = False
            for item_group in root.findall('msbuild:ItemGroup', ns):
                cond = item_group.get('Condition')
                if cond and cond == f"'$(Configuration)' == '{conf}'":
                    found = True
                    break
            if not found:
                if conf.startswith(base_prefix):
                    folder_file = conf
                else:
                    folder_file = f"{base_prefix}{conf}"
                new_item_group = ET.Element(f'{{{MSBUILD_NS}}}ItemGroup', Condition=f"'$(Configuration)' == '{conf}'")
                pr = ET.SubElement(
                    new_item_group,
                    f'{{{MSBUILD_NS}}}ProjectReference',
                    Include=f"{prefix}{folder_file}\\{folder_file}.{ext}"
                )
                root.append(new_item_group)

    backup_path = file_path + ".bak"
    if not os.path.exists(backup_path):
        os.rename(file_path, backup_path)

    indent(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)
    fix_project_tag_order_and_xml_decl(file_path)

def process_folder(bom_name):
    folder_path = os.path.abspath(os.path.join(os.getcwd(), '..', '..', '..'))
    updated_files = []
    for ext in ('*tproj', '*tpproj'):
        for file_path in glob.glob(os.path.join(folder_path, '**', ext), recursive=True):
            # Skip .tpproj files under Shared/POR_TP (case-insensitive, handles both / and \)
            norm_path = file_path.replace("\\", "/").lower()
            filename = os.path.basename(file_path)
            is_mtproj = filename.lower().endswith('.mtproj')
            if ext == '*tpproj' and '/shared/por_tp/' in norm_path:
                continue
            if is_mtproj and not has_project_configuration(file_path):
                print(f"Skipping (no <ProjectConfiguration>): {file_path}")
                continue
            print(f"Processing: {file_path}")
            add_bom_to_tproj(file_path, bom_name)
            updated_files.append(file_path)
    for file_path in updated_files:
        bak_path = file_path + ".bak"
        if os.path.exists(bak_path):
            try:
                os.remove(bak_path)
                print(f"Deleted backup: {bak_path}")
            except Exception as e:
                print(f"Could not delete {bak_path}: {e}")
    print("Update complete.")

if __name__ == "__main__":
    bom_name = input("Enter BOM name: ").strip()
    process_folder(bom_name)