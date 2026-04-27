namespace TDAU
{
	using System;
	using System.Collections.Generic;
	using Prime.ConsoleService;
	using Prime.DatalogService;
    using Prime.DatalogService.DatalogSpec;
    using Prime.ThermalService;
	public class TDAUIdeality
	{
		public string TDAUIdealityCalc()
		{
			var console = Prime.Services.ConsoleService;
			var context = Prime.Services.SessionService.GetCurrentThreadSessionContextContainer();

			var tdauPins = new List<string>();
			tdauPins.Add("IPC::CPU_TDAU0");
            tdauPins.Add("IPH::HUB_TDAU0");
            tdauPins.Add("IPG::GCD_TDAU0");
            
			//tdauPins.Add("TDIODE_CORE_SEC");
            string print;
            double ideality;
            double setpoint = 0;
            double hot_ideality = 0;
            double cold_ideality = 0;
            setpoint = Convert.ToInt32(Prime.Services.UserVarService.GetStringValue("SCVars.SC_TEMPERATURE"));
            foreach (var pin in tdauPins)
            {               
                if (pin == "IPC::CPU_TDAU0" && Prime.Services.UserVarService.GetStringValue("IF_18AP") == "NO")
                {
                    hot_ideality = 1.0029;
                    cold_ideality = 1.0015;
                }
                else
                {
                    hot_ideality = 1.13;
                    cold_ideality = 1.165;
                }
                var parametricData = Prime.Services.ThermalService.TdauGetParametricValues(pin);
                
				Prime.Services.ConsoleService.PrintDebug(() => "TDAU pin name:" + pin, context);
                Prime.Services.ConsoleService.PrintDebug(() => "hot_ideality:" + hot_ideality, context);
                Prime.Services.ConsoleService.PrintDebug(() => "cold_ideality:" + cold_ideality, context);
                var Vbe3 = parametricData[0].GetVbeIe3();
                var Vbe1 = parametricData[0].GetVbeIe1();
                var Ie3  = parametricData[0].GetIeValIe3();
                var Ie1  = parametricData[0].GetIeValIe1();
                var Temp = parametricData[0].GetTemperature();
				if (Prime.Services.UserVarService.GetStringValue("SCVars.SC_CURRENT_PROCESS_STEP") == "CLASSHOT" || Prime.Services.UserVarService.GetStringValue("SCVars.SC_CURRENT_PROCESS_STEP") == "PHMHOT") {
                    ideality = (hot_ideality * (Temp + 273.15)) / (273.15 + setpoint);
                    print = "ideality_CH|PHM";
				}
                else {
                    ideality = (cold_ideality * (Temp + 273.15)) / (273.15 + setpoint);
                    print = "ideality_OTHERS";
				}				
                //var ideality = ((1.60217646e-19)/(1.3806503e-23 * 378.15))*((Vbe3-Vbe1)/(Math.Log(Ie3/Ie1)));
				Prime.Services.ConsoleService.PrintDebug(() => "ideality:" + ideality, context);
                Prime.Services.ConsoleService.PrintDebug(() => "ideality:" + print, context);
                Prime.Services.UserVarService.SetValue("__shared__::PTHVars", pin.Substring(5,9) + "_IDEALITY", ideality);
            }

            return "1";
		}
	}
}
