namespace FlowBasedRouter
{
    using System;
    using Prime.ConsoleService;
    using Prime.SessionService;
    using Prime.SharedStorageService;
    using Prime.DffService;
    using Prime.TestProgramService;
    using System.Linq;
    using System.Collections.Generic;

    public class FlowBasedRouter
    {
        public string CPUFlowBasedRouter()
        {
            try
            {
                var flowNumber = Prime.Services.MultiTrialService.GetTrialVariableCurrentValue("IPC::CPU_TRIALS::FlowDomain", "ATOM_TOP");

                string flownumStr = flowNumber.ToString();
                Prime.Services.ConsoleService.Print($"Flow number for ATOM_TOP currently is {flownumStr}");

                if (flowNumber == 0)
                {
                    // Return port 1 if flowNuber == 0
                    return "1";
                }
                else if (flowNumber == 1)
                {
                    // Return port 2 if flowNuber == 1
                    return "2";
                }
                else
                {
                    return "3";
                }
            }
            catch (Exception ex)
            {
                // Handle the exception to avoid overkill
                Prime.Services.ConsoleService.Print(ex.Message);
                return "1";
            }
        }
    }
}