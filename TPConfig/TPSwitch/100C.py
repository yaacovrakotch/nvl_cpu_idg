from mod.tpswitch import TPSwitch

# place xls in common repo: BaseInputs/Inputs/POR_TP/Class_NVL_S28C/CLASS_NVL_S28C.xlsx.100C
obj = TPSwitch('POR_TP/Class_NVL_S28C/CLASS_NVL_S28C.xlsx')
obj.overwrite_with('Shared/BaseInputs/Inputs/CLASS_NVL_S28C.xlsx.100C')

# place xls in common repo: BaseInputs/Inputs/POR_TP/Class_NVL_S52C/CLASS_NVL_S52C.xlsx.100C
obj = TPSwitch('POR_TP/Class_NVL_S52C/CLASS_NVL_S52C.xlsx')
obj.overwrite_with('Shared/BaseInputs/Inputs/CLASS_NVL_S52C.xlsx.100C')

obj = TPSwitch('Shared/BaseInputs/Common/Common_Files/SCVars.usrv')
obj.search_replace('String SC_TEMPERATURE = "80"', 'String SC_TEMPERATURE = "100"')
obj.write()

obj = TPSwitch('Shared/BaseInputs/Common/Common_Files/common.usrv')
obj.search_replace('"80"', '"100"')
obj.write()

# place 100C in Modules/PTH/PTH_DIODE_XXX/InputFiles/MTL_CLASS_BT_CHECK.txt.100C
obj = TPSwitch("Shared/Modules/PTH/PTH_DIODE_XXX/InputFiles/MTL_CLASS_BT_CHECK.txt")
obj.overwrite_with("Shared/BaseInputs/Inputs/MTL_CLASS_BT_CHECK.txt.100C")

