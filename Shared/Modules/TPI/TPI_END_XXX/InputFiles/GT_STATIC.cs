namespace TPIUserCode
{
    using System;
    using System.Linq;
    using System.Collections.Generic;
    using System.Text.RegularExpressions;
    using Prime.ConsoleService;
    using Prime.DatalogService;
    using Prime.DffService;
    using Prime.PlatformService;
	using Prime.UserVarService;
	using Prime.SharedStorageService;
	using Prime.SessionService;
    using Prime.TestProgramService;

    public class TPI
    {
        public string PoweronGTStaticValue()
        {
            var SessionContext = Prime.Services.SessionService.GetCurrentThreadSessionContextContainer();
            var writer = Prime.Services.DatalogService.GetItuffStrgvalWriter();
            string upsvf;
            
            upsvf = "GT:2.6^0.853%2.2^0.773%2^0.725%1.5^0.605%1.2^0.566_GTVPG:2.6^0.853%2.2^0.773%2^0.725%1.5^0.605%1.2^0.566";
            Prime.Services.SharedStorageService.InsertRowAtTable("UPSVFPASSFLOW_U1PU4", upsvf,Context.DUT, Prime.SharedStorageService.ResetPolicy.RESET_AT_DEVICE_START, SessionContext);
            
            // Prime.Services.SharedStorageService.InsertRowAtTable("GTSREC", "0000000000000000000000000",Context.DUT, Prime.SharedStorageService.ResetPolicy.RESET_AT_DEVICE_START, SessionContext);
                 
            // var PrintGSDS = Prime.Services.SharedStorageService.GetRowFromTable<string>("UPSVFPASSFLOW_U1PU4", Context.DUT, SessionContext);
            // Prime.Services.ConsoleService.PrintDebug(() => PrintGSDS, SessionContext);
            
            // writer.SetTnamePostfix("_NO_TOKENS");
            // writer.SetData("No_Tokens_Filtred");
            // Prime.Services.DatalogService.WriteToItuff(writer, SessionContext);
            
            return "1";
        }
    }
}