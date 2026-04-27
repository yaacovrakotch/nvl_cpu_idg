import sys
from pathlib import Path


def main():
    # Gets current working directory
    current_dir = Path.cwd()

    # Goes up 4 parent directories
    target_dir = current_dir
    for _ in range(4):
        target_dir = target_dir.parent

    # Print that directory
    print(f"Target directory:\n{target_dir}\n")

    # -------------------------------------------------
    # Edit PLIST file
    # -------------------------------------------------
    plist_path = target_dir / "POR_TP" / "Class_NVL_S28C" / "PLIST_ALL_IPC.plist.ipxml"

    if not plist_path.exists():
        print(f"ERROR: PLIST file not found:\n{plist_path}")
        input("Press Enter to exit...")
        sys.exit(1)

    print("PLIST file exists.")

    with open(plist_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = [
        '<PListFile name="arr_cdie_mbist_ccf_class_raster_autoinc_tap_allplist.plist" />',
        '<PListFile name="arr_cdie_mbist_core_class_raster_autoinc_all_tap_allplist.plist" />',
        '<PListFile name="arr_cdie_mbist_uncore_class_raster_autoinc_tap_allplist.plist" />',
        '<PListFile name="arr_cdie_x_pbist_atom_all_vatom_raster_cb_f1_tito_class.plist" />',
        '<PListFile name="arr_cdie_x_pbist_atom_all_vatom_raster_f1_tito_class.plist" />',
        '<PListFile name="arr_cdie_x_pbist_atom_all_vatom_raster_xr_f1_tito_class.plist" />'
    ]

    content_str = "".join(lines)

    # Determine which entries are missing
    missing_entries = [e for e in entries if e not in content_str]

    if not missing_entries:
        print("All PList entries already exist. Skipping insert.")
    else:
        insert_lines = [f'        {entry}\n' for entry in missing_entries]

        for i, line in enumerate(lines):
            if "</PList>" in line:
                lines = lines[:i] + insert_lines + lines[i:]
                break
        else:
            print("ERROR: </PList> tag not found.")
            input("Press Enter to exit...")
            sys.exit(1)

        with open(plist_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"Inserted {len(missing_entries)} missing PList entries.")

    # -------------------------------------------------
    # Edit MTPL file
    # -------------------------------------------------
    mtpl_path = target_dir / "Modules" / "QNR" / "QNR_CARV_CKX" / "QNR_CARV_CKX.mtpl"

    if not mtpl_path.exists():
        print(f"ERROR: MTPL file not found:\n{mtpl_path}")
        input("Press Enter to exit...")
        sys.exit(1)

    print("MTPL file exists.")

    with open(mtpl_path, "r", encoding="utf-8") as f:
        content = f.read()

    old_text = "./InputFiles/NVL_ARV_CPU.json"
    new_text = "./InputFiles/NVL_ARV_CPU_DBG.json"

    if new_text in content:
        print("MTPL already updated. Skipping replace.")
    else:
        if old_text not in content:
            print("ERROR: Original JSON reference not found.")
            input("Press Enter to exit...")
            sys.exit(1)

        content = content.replace(old_text, new_text)

        with open(mtpl_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("MTPL updated.")

    # -------------------------------------------------
    print("\ndone")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
