@echo off
python I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/pymtpl.py %1/POR_TP/Class_DNL_S28C/ProgramFlowsTestPlan/IPC_FLOWS.py -env %1/POR_TP/Class_DNL_S28C/EnvironmentFile.env"
SET DIE_LIST=CPU
python I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/pymtpl.py %1/Shared/POR_TP/Class_DNL_S28C/ProgramFlowsTestPlan/ProgramFlows.py -env %1/POR_TP/Class_DNL_S28C/EnvironmentFile.env"
