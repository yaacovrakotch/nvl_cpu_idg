from mod.tpswitch import TPSwitch

# Swap the RecipeSettings.xlsx file with a copy set to 80C
obj = TPSwitch('Shared/BaseInputs/Common/Common_Files/RecipeSettings.xlsx')
obj.overwrite_with('Shared/BaseInputs/Inputs/RecipeSettings.xlsx.80C')

# Set UserVars from 100 to 80
obj = TPSwitch('Shared/BaseInputs/Common/Common_Files/SCVars.usrv')
obj.search_replace('String SC_TEMPERATURE = "100"', 'String SC_TEMPERATURE = "80"')
obj.write()

obj = TPSwitch('Shared/BaseInputs/Common/Common_Files/common.usrv')
obj.search_replace('"100"', '"80"')
obj.write()

# Set HOT temps from 100 to 80
obj = TPSwitch("Shared/Modules/PTH/PTH_DIODE_XXX/InputFiles/MTL_CLASS_BT_CHECK.txt")
obj.overwrite_with("Shared/BaseInputs/Inputs/MTL_CLASS_BT_CHECK.txt.80C")

# Loosen SHOPS limits
obj = TPSwitch("Shared/Modules/TPI/TPI_SHOPS_XKPKGDT/TPI_SHOPS_XKPKGDT.usrv")
obj.overwrite_with("Shared/BaseInputs/Inputs/TPI_SHOPS_XKPKGDT.usrv.80C")
