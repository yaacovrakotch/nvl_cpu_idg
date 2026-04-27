namespace TosUtil
{
    using System;
    using System.Diagnostics;
	using System.IO;
  	using Prime.ConsoleService;
    using Prime.TestProgramService;
    using Prime.PlatformService;
    using Prime.UserVarService;
	using Prime.FileService;


    public class Logging
    {
        private string ExecuteCommandAsync(string arguments)
        {
            var tos = Prime.Services.PlatformService.Utils.GetTOSRootFullPath();
            
            // Create process start info
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = $"{tos}\\runtime\\release\\singlescriptcmd.exe",
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
     
            // Start the process without waiting
            Process.Start(startInfo);            
            Prime.Services.ConsoleService.Print($"Command started asynchronously: {arguments}");
            
            return "1";
        }

        private string ExecuteCommand(string arguments)
        {
            var tos = Prime.Services.PlatformService.Utils.GetTOSRootFullPath();
            
            // Create process start info
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = $"{tos}\\runtime\\release\\singlescriptcmd.exe",
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
     
            // Start the process
            using (Process process = Process.Start(startInfo))
            {
                // Read output
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                
                // Wait for exit
                process.WaitForExit();
                
                // Display results
                Prime.Services.ConsoleService.Print($"output: {output}");
                
                if (!string.IsNullOrEmpty(error))
                {
                    Prime.Services.ConsoleService.Print($"error: {error}");
                }
                
                Prime.Services.ConsoleService.Print($"Exit Code: {process.ExitCode}");
                
                return process.ExitCode == 0 ? "1" : "0";
            }
        }

        private void CompressFile(string sourceFile, string destinationFile)
        {
             string safeSource = sourceFile.Replace("'", "''");
             string safeDest = destinationFile.Replace("'", "''");
             
             string psCommand = $"Add-Type -AssemblyName System.IO.Compression; $s=[System.IO.File]::OpenRead('{safeSource}'); $d=[System.IO.File]::Create('{safeDest}'); $g=New-Object System.IO.Compression.GZipStream($d,[System.IO.Compression.CompressionMode]::Compress); $s.CopyTo($g); $g.Dispose(); $d.Dispose(); $s.Dispose();";

             ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = "powershell.exe",
                Arguments = $"-NoProfile -Command \"{psCommand}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = Process.Start(startInfo))
            {
                process.WaitForExit();
                if (process.ExitCode != 0)
                {
                     string error = process.StandardError.ReadToEnd();
                     Prime.Services.ConsoleService.Print($"Compression failed: {error}");
                }
            }
        }

        public string Export_Start()
        {
            string outputPath = "c:\\temp\\consolelog.txt";           
            return ExecuteCommandAsync($"StartConsolidatedLogging {outputPath} True True");
        }

        public string Export_Stop()
        {
			var testBoardId = Prime.Services.UserVarService.GetStringValue("SCVars.TP_TESTBOARD_ID").Replace(":", "_");
            var siteId = Prime.Services.UserVarService.GetStringValue("SCVars.SC_SITEID").Replace(":", "_");
            var lotId = Prime.Services.UserVarService.GetStringValue("SCVars.SC_LOTNAME").Replace(":", "_");
            
            System.Threading.Tasks.Task.Run(() =>
            {
                // Generate timestamped filename
                string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            
                // Verify the log file was created
                if (!File.Exists("c:\\temp\\consolelog.txt"))
                {
                    ExecuteCommand("stopConsolidatedLogging"); // Ensure logging is stopped even if file is missing
                    Prime.Services.ConsoleService.Print("Console log file was not created");
                    return;
                }
                
                string logFileName = $"{lotId}_{testBoardId}_{siteId}_{timestamp}_log.txt.gz";
                string tempConsoleLog = "c:\\temp\\consolelog.txt";
                string tempCompressedPath = $"c:\\temp\\{logFileName}";

                // it is case-sensitive: stopConsolidatedLogging.
                ExecuteCommand("stopConsolidatedLogging");

                // Compress the file using PowerShell helper
                CompressFile(tempConsoleLog, tempCompressedPath);

                if (Prime.Services.FileService.IsSysCFileServiceUp())
                {
                    Prime.Services.ConsoleService.Print($"Transferring file {logFileName} via SysC.");
                    Prime.Base.ServiceStore<Prime.PlatformService.Internal.IPlatformService>.Service.File.PushFileViaSysC($"c:\\temp", logFileName, $"I:\\engineering\\dev\\team_pdx_client_ccr\\users\\ATE_Log\\", 100);
                }
                else
                {
                    Prime.Services.ConsoleService.Print($"SysC is not enabled. Transferring local file {logFileName} through direct copy.");
                    File.Copy(tempCompressedPath, $"I:\\engineering\\dev\\team_pdx_client_ccr\\users\\ATE_Log\\{logFileName}", overwrite: true);
                }

                if (File.Exists(tempCompressedPath))
                {
                    File.Delete(tempCompressedPath);
                }
                if (File.Exists(tempConsoleLog))
                {
                    File.Delete(tempConsoleLog);
                }
            });

			return "1";
        }

        public string Console_Print()
        {
            var vid = Prime.Services.UserVarService.GetStringValue("SCVars.SC_VISUALID");
            var locationid = Prime.Services.UserVarService.GetStringValue("SCVars.SC_LOCN");
            var Stepid = Prime.Services.UserVarService.GetStringValue("SCVars.SC_CURRENT_PROCESS_STEP");
			var testBoardId = Prime.Services.UserVarService.GetStringValue("SCVars.TP_TESTBOARD_ID").Replace(":", "_");
            var siteId = Prime.Services.UserVarService.GetStringValue("SCVars.SC_SITEID").Replace(":", "_");
            var lotId = Prime.Services.UserVarService.GetStringValue("SCVars.SC_LOTNAME").Replace(":", "_");
            var engId = Prime.Services.UserVarService.GetStringValue("SCVars.SC_ENGID").Replace(":", "_");
           
            Prime.Services.ConsoleService.Print( "VID:" + vid);
            Prime.Services.ConsoleService.Print( "Location_ID:" + locationid);
            Prime.Services.ConsoleService.Print( "Sub_Step_ID:" + Stepid);
            Prime.Services.ConsoleService.Print( "TestBoard_ID:" + testBoardId);
            Prime.Services.ConsoleService.Print( "Site_ID:" + siteId);
            Prime.Services.ConsoleService.Print( "Lot_ID:" + lotId);
            Prime.Services.ConsoleService.Print( "Eng_ID:" + engId);
            return "1";
        }
    }
}