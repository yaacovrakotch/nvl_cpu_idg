namespace TPINFO
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Prime.ConsoleService;
    using Prime.DatalogService;
    using Prime.SessionService;
    using Prime.TelemetryService;

    public class Telemetry
    {
        public string LogLoadedItems()
        {
            var context = Prime.Services.SessionService.GetCurrentThreadSessionContextContainer();
            var logger = new TelemetryHandler<Telemetry>(TelemetryLogLevelResolver.TelemetryLogLevel.Debug);

            var allInstances = Prime.Services.PlatformService.TestPlan.GetAllTestInstanceNames();
            var allPlists = Prime.Services.PlatformService.Plist.GetAllPlists();

            Prime.Services.ConsoleService.PrintDebug(() => "Logging Instances and Plists to Prime Telemetry.", context);
            Prime.Services.ConsoleService.PrintDebug(() => "Requires environment variable 'PRIME_IS_TELEMETRY_ENABLED' set to 'TRUE'.", context);
            logger.LogUsage(() => new Dictionary<string, string>
            {
                { "TestInstances", string.Join(",", allInstances) },
                { "PLists", string.Join(",", allPlists) },
            });

            Prime.Services.ConsoleService.PrintDebug(() => "Done logging telemetry.", context);
            return "1";
        }
    }
}
