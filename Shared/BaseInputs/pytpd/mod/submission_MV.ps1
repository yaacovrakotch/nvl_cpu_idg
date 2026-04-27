param (
	[Parameter(Mandatory)]
    [string]$UserName,
	[Parameter(Mandatory)]
    [string]$Password,
    [string]$JsonFilePath,
    [Parameter(Mandatory)]
    [string]$OutputDirectory,
    [string]$submission_MV,
    [string]$GetData,
    [string]$SubmissionFilePath,
    [string]$ReportFilePath
)

#---------------------------------------------------------------------#  
# Name: Get-Token                                                     #
# Summary: Take the following actions:                                #
#    1. Generate Azure AD token                                       #
#    2. Send token to SPARK for authentication                        #
#       SPARK returns a token if authentication finished successfully #
#---------------------------------------------------------------------#
function Get-Token {
  param (
      [Parameter(Mandatory = $true)]
      [string] $TenantId
    , [Parameter(Mandatory = $true)]
      [string] $ClientId
    , [Parameter(Mandatory = $true)]
      [string] $UserName
    , [Parameter(Mandatory = $true)]
      [string] $Password
  )
 
  Try
  {
    $Uri = ('https://login.microsoftonline.com/{0}/oauth2/v2.0/token' -f $TenantId)
    $Form = @{
        grant_type      = 'password'
        client_id       = $ClientId
        scope           = 'api://b82c0403-5aa9-48bf-9c57-d3deba881d82/access_as_user'
        username        = $UserName
        password        = $Password
    }
    $AzureResult = Invoke-RestMethod -Uri $Uri -Method Post -Body $Form -ErrorAction Stop
  }
  Catch
  {
    $ErrorMessage = 'Failed to acquire Azure AD token.'
    Write-Error -Message "$ErrorMessage Details: $_"
    Exit(-1)
  }

  Try
  {
      $sparkAuthenticationUri = 'https://spark-api.app.intel.com/api/v1/auth/token?accessToken={0}' -f $AzureResult.access_token
      $SparkResult = Invoke-RestMethod $sparkAuthenticationUri -ErrorAction Stop
  }
  Catch
  {
      $ErrorMessage = 'Failed to acquire SPARK token.'
      Write-Error -Message "$ErrorMessage Details: $_"
      Exit(-1)
  }

  return $SparkResult.token 
}

#---------------------------------------------------------------------#  
# Name: Create-Dto                                                    #
# Summary: Read the json file with the submission content             #
#---------------------------------------------------------------------#
function Create-Dto {
 param (
      [Parameter(Mandatory = $true)]
      [string] $JsonFilePath
  )

 Try
  {
      $json = Get-Content -Raw -Path $JsonFilePath #| ConvertFrom-Json
  }
  Catch
  {
      $ErrorMessage = 'Failed to read json file content.'
      Write-Error -Message 'Failed to read json file content.'
      Exit(-1)
  }
  return $json
}

#---------------------------------------------------------------------#  
# Name: Submit                                                        #
# Summary: Send the submission Dto to SPARK API                       #
#---------------------------------------------------------------------#
function Submit {
  param (
      [Parameter(Mandatory = $true)]
      [string] $SparkToken,
      [Parameter(Mandatory = $true)]
      [string] $Dto
  )
  
  Try
  {
      $Uri = 'https://spark-api.app.intel.com/api/v1/experiment-groups'
      $headers = @{
        Authorization="Bearer $SparkToken"
      }
      $response = Invoke-RestMethod $Uri -Method Post -headers $headers -Body $Dto -ContentType 'application/json' -ErrorAction Stop
  }
  catch [System.Net.WebException] { 
    Write-Host -Foreground Red -Background Black 'Failed to submit experiments with SPARK.'
    Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ 
    Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription

    #Get body of message
    $streamReader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $hashtable = @{}
    ($streamReader.ReadToEnd() | ConvertFrom-Json).psobject.properties | Foreach { $hashtable[$_.Name] = $_.Value }
    $streamReader.Close()
    $hashtable | Format-Table -Wrap -AutoSize
    Exit(-1)
  } 
  Catch
  {
      Write-Host('Failed to submit experiments with SPARK.')
      Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ 
      Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription
      Write-Host "StatusDescription:" $_.Exception.Message
      Exit(-1)
  }
  return $response 
}

#---------------------------------------------------------------------#  
# Name: GetExperiments                                                #
# Summary: Get Experiments using SPARK API                            #
#---------------------------------------------------------------------#
function GetExperiments {
    param (
        [Parameter(Mandatory = $true)]
        [string] $SparkToken,
        [string] $submissionID
    )

    Try {
        $Uri = "https://spark-api.app.intel.com/api/v1/experiment-groups/$submissionID"
        $headers = @{
            Authorization = "Bearer $SparkToken"
        }
        $response = Invoke-RestMethod $Uri -Method Get -headers $headers -ContentType 'Application/json' -ErrorAction Stop
    } Catch {
        Write-Error -Message "Failed to get experiments with SPARK. Details: $_"
        Exit(-1)
    }
    return $response
}

#---------------------------------------------------------------------#  
# Name: SubmitAction                                                #
# Summary: Submit experiments using SPARK API                        #
#---------------------------------------------------------------------#
function SubmitAction {
    param (
        [Parameter(Mandatory = $true)]
        [string] $TenantId,
        [Parameter(Mandatory = $true)]
        [string] $ClientId
    )
    # Check if credentials are retrieved successfully
    if (-not $UserName -or -not $Password) {
        Write-Error "Environment variables SPARK_USERNAME and SPARK_PASSWORD must be set."
        Exit(-1)
    }

    Write-Host('Generating SPARK token')
    $SparkToken = Get-Token -TenantId $TenantId -ClientId $ClientId -UserName $UserName -Password $Password
    Write-Host('Generating SPARK token - done')
    Write-Host('Reading json file')
    $Dto = Create-Dto -JsonFilePath $JsonFilePath
    Write-Host('Reading json file - done')
    Write-Host('Submiting new experiments with SPARK API')
    $SubmissionResult = Submit -SparkToken $SparkToken -Dto $Dto
    Write-Host('Submiting new experiments with SPARK API- done')
    Write-Host('Submitted experiment group:')
    Write-Host($SubmissionResult)

    # Ensure the output directory exists
    if (-not (Test-Path -Path $OutputDirectory)) {
        New-Item -Path $OutputDirectory -ItemType Directory
    }

    # Clear the submission_id.txt in the output directory
    $SubmissionIdFilePath = Join-Path $OutputDirectory 'submission_id.txt'
    # if (Test-Path -Path $SubmissionIdFilePath) {
    #     Write-Output "Clear the submission_id.txt"
    #     Clear-Content $SubmissionIdFilePath
    # }

    foreach ($_ in $SubmissionResult){
        if ($_ -match "id"){
            $id = $_.id
            $name = $_.username
            $tpname = $_.testProgramData.tpName
            $currentDateTime = Get-Date
            Write-Output "$id $name $currentDateTime $tpname" >> $SubmissionIdFilePath
        }
    }
}

#---------------------------------------------------------------------#  
# Name: GetDataAction                                                #
# Summary: Get data using SPARK API                                   #
#---------------------------------------------------------------------#
function GetDataAction {

    if (-not $UserName -or -not $Password) {
        Write-Error "Environment variables SPARK_USERNAME and SPARK_PASSWORD must be set."
        Exit(-1)
    }

    Write-Host 'Generating SPARK token'
    $SparkToken = Get-Token -TenantId $TenantId -ClientId $ClientId -UserName $UserName -Password $Password
    Write-Host 'Generating SPARK token - done'

    # Ensure the output directory exists
    if (-not (Test-Path -Path $OutputDirectory)) {
        New-Item -Path $OutputDirectory -ItemType Directory
    }

    # Clear the output.txt in the output directory
    $OutputFilePath = Join-Path $OutputDirectory 'output.txt'
    Write-Host "Output file path: $OutputFilePath"
    if (Test-Path -Path $OutputFilePath) {
        Write-Output "Clearing the output.txt"
        Clear-Content $OutputFilePath
    }

    # Read the report file to get TestProgram, ContactEmail, Lot, Qty, Operation, EngID, and Ref_VPO
    Write-Host "Reading report file from: $ReportFilePath"
    Try {
        $report_data = Get-Content -Path $ReportFilePath
    } Catch {
        Write-Error -Message "Failed to read the report file. The file does not exist. Details: $_"
        Exit(-1)
    }

    # Parse the report file to extract TestProgram, Lot, Qty, Operation, EngID, and Ref_VPO
    $report_map = @{}
    $contact_emails_set = @{}  # Use a hashtable to avoid duplicates
    $testProgram = ""
    foreach ($line in $report_data) {
        if ($line -match "TestProgram: (.+)") {
            $testProgram = $matches[1]
        }
        elseif ($line -match "ContactEmail: (.+)") {
            $contactEmails = $matches[1]
            $contact_emails_set[$contactEmails] = $true  # Add to hashtable to avoid duplicates
        }
        elseif ($line -match "^(.+?)-(.+?)-(.+?)-(.+?)-(.+?)-(.+?)-(.+)$") {  # Updated regex to capture 7 parts including Ref_VPO
            $displayName = $matches[1]
            $lot = $matches[2]
            $qty = $matches[3]
            $operation = $matches[4]
            $engID = $matches[5]
            $tags = $matches[6]
            $refVPO = $matches[7]  # Capture Ref_VPO
            $report_map[$displayName] = @{
                Lot = $lot
                Qty = $qty
                Operation = $operation
                EngID = $engID
                Tags = $tags
                RefVPO = $refVPO  # Store Ref_VPO
            }
            Write-Host "Read DisplayName from report_info.txt: $displayName with Ref_VPO: $refVPO"
        }
    }

    # Write TestProgram and ContactEmail at the top of the output file
    Write-Output "TestProgram: $testProgram" >> $OutputFilePath
    $emailTo = $contact_emails_set.Keys -join ","
    Write-Output "ContactEmail: $emailTo" >> $OutputFilePath

    # Getting submission IDs
    Write-Host "Reading submission file from: $SubmissionFilePath"
    Try {
        $submission_ids = Get-Content -Path $SubmissionFilePath
    } Catch {
        Write-Error -Message "Failed to read the submission file. The file does not exist. Details: $_"
        Exit(-1)
    }

    # Iterate over each submission ID and extract VPO information
    foreach ($submission in $submission_ids) {
        $submissionID = $submission.Split(' ')[0]
        Write-Host "Processing submission ID: $submissionID"

        $GetResult = GetExperiments -SparkToken $SparkToken -submissionID $submissionID
        $jout = $GetResult | ConvertTo-Json -Depth 6
        $myJson = $jout | ConvertFrom-Json
        Write-Host "Experiment Group ID: " $myJson.id
        $myVPOinfo = @()

        foreach ($_ in $myJson.experiments) {
            $experiment = @{}
            $experiment['vpo'] = $_.vpo
            $experiment['DisplayName'] = $_.displayName  # Add DisplayName to the experiment info
            $experiment['Tags'] = $_.tags -join ", "
        if ($qty -eq '0') {
            Write-Host "Qty is $qty. Trying to get the correct numberOfUnitsToRun."
            Write-Host "Debug - material property: $($_.material)"
            Write-Host "Debug - material.lots property: $($_.material.lots)"
            if ($_.material -and $_.material.lots -and $_.material.lots.numberOfUnitsToRun) {
                $experiment['qty'] = $_.material.lots.numberOfUnitsToRun
                Write-Host "New numberOfUnitsToRun is $($experiment['qty'])."
            } else {
                Write-Host "Warning: numberOfUnitsToRun not found or is null"
                $experiment['qty'] = "0"  # Default value
            }
        } else {
            $experiment['qty'] = $qty  # Use the original qty if it's not '0'
        }
        Write-Host "VPO: " $_.vpo
        Write-Host "DisplayName: " $_.displayName  # Log DisplayName
        $myVPOinfo += $experiment
        }

        # Write initial data to output file
        foreach ($experiment in $myVPOinfo) {
            Write-Output "DisplayName: $($experiment['DisplayName']) -- VPO: $($experiment['vpo']) -- Ref_VPO: -- Lot: -- Qty: -- Operation: -- EngID: -- Tags: $($experiment['Tags'])" >> $OutputFilePath
        }
    }

    # Update output file with Lot, Qty, Operation, EngID, and Ref_VPO from report_info.txt
    $output_lines = Get-Content -Path $OutputFilePath
    Clear-Content -Path $OutputFilePath

    # Write TestProgram and ContactEmail again at the top after clearing content
    Write-Output "TestProgram: $testProgram" >> $OutputFilePath
    Write-Output "ContactEmail: $emailTo" >> $OutputFilePath

    foreach ($line in $output_lines) {
        if ($line -match "DisplayName: (.+?) -- VPO: (.+?) -- Ref_VPO: -- Lot: -- Qty: -- Operation: -- EngID: -- Tags: (.+?)$") {
            $displayName = $matches[1]
            $vpo = $matches[2]
            $tags = $matches[3]

            Write-Host "Comparing DisplayName from output.txt: $displayName"

            if ($report_map.ContainsKey($displayName)) {
                $report_info = $report_map[$displayName]
                # Check if we have an updated qty from the experiment data
                $qtyToUse = $report_info['Qty']
                foreach ($experiment in $myVPOinfo) {
                    if ($experiment['DisplayName'] -eq $displayName -and $experiment['qty'] -ne "0" -and $experiment['qty'] -ne $null) {
                        $qtyToUse = $experiment['qty']
                        Write-Host "Updated Qty for $displayName from $($report_info['Qty']) to $qtyToUse"
                        break
                    }
                }
                Write-Output "DisplayName: $displayName -- VPO: $vpo -- Ref_VPO: $($report_info['RefVPO']) -- Lot: $($report_info['Lot']) -- Qty: $qtyToUse -- Operation: $($report_info['Operation']) -- EngID: $($report_info['EngID']) -- Tags: $tags" >> $OutputFilePath
            } else {
                Write-Output "DisplayName: $displayName -- VPO: $vpo -- Ref_VPO: -- Lot: -- Qty: -- Operation: -- EngID: -- Tags: $tags" >> $OutputFilePath
                Write-Error "No matching report info found for DisplayName: $displayName"
            }
        }
    }

    Write-Host "Email will be sent to: $emailTo"
    Write-Host "Completed Spark Automation Script"

}

$TenantId = '46c98d88-e344-4ed4-8496-4ed7712e255d'
$ClientId = 'b82c0403-5aa9-48bf-9c57-d3deba881d82'
if ($submission_MV -eq 'true') {
    [void](SubmitAction -TenantId $TenantId -ClientId $ClientId)
}
elseif ($GetData -eq 'true') {
    [void](GetDataAction -TenantId $TenantId -ClientId $ClientId)
}