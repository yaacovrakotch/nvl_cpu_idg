#----------------------------------------------------------------------------------------
#
# This .tpl file is designed to be used for several test programs in the solution.
# Any change to this file should be verified with all test programs.
#
#----------------------------------------------------------------------------------------

Version 1.0;

ProgramStyle = Modular;

TestPlan BASE;

Import "common.imp";
Import "common_SubBindef.imp";
Import "Common_BOM.imp";
Import "IPC_SubBindef.imp";
Import "cpu_pkg_base.imp";


#Common_SubBindef

EndSequence
{
	Power_dwn_PKG_xxx_pwrd_zerzer
}

