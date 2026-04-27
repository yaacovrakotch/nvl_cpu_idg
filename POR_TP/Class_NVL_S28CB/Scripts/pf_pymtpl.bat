@echo off
python I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/pymtpl.py %1/POR_TP/Class_NVL_S28CB/ProgramFlowsTestPlan/IPC_FLOWS.py -env %1/POR_TP/Class_NVL_S28CB/EnvironmentFile.env"
SET DIE_LIST=CPU
python I:/tpvalidation/engtools/tptools/mtl/beta/gen1/main/pymtpl.py %1/Shared/POR_TP/Class_NVL_S28CB/ProgramFlowsTestPlan/ProgramFlows.py -env %1/POR_TP/Class_NVL_S28CB/EnvironmentFile.env"
