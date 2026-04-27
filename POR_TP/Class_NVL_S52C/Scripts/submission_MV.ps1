param (
    #[Parameter(Mandatory)]
    #[string]
    # $UserName
   # ,[Parameter(Mandatory)]
    # [string]
    # $Password
   [Parameter(Mandatory)]
    [string]
    $JsonFilePath
)


#---------------------------------------------------------------------#  
# Name: Get-Token                                                     #
# Summary: Take the following actions:                                #
#    1. Generate Azure AD token                                       #
#    2. Send token to SPARK for authentication                        #
#       SPARK returns a token if authentication finishde successfully #
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
		grant_type  	= 'password'
		client_id   	= $ClientId
		scope 		= 'api://b82c0403-5aa9-48bf-9c57-d3deba881d82/access_as_user'
		username 	= $UserName
		password 	= $Password
	}
	$AzureResult = Invoke-RestMethod -Uri $Uri -Method Post -Body $Form
  }
  Catch
  {
	$ErrorMessage = 'Failed to aquire Azure AD token.'
	Write-Error -Message 'Failed to aquire Azure AD token'
    Exit(-1)
  }

  Try
  {
	  $sparkAuthenticationUri = 'https://spark-api.app.intel.com/api/v1/auth/token?accessToken={0}' -f $AzureResult.access_token
	  $SparkResult = Invoke-RestMethod $sparkAuthenticationUri
  }
  Catch
  {
	  $ErrorMessage = 'Failed to aquire SPARK token.'
	  Write-Error -Message 'Failed to aquire SPARK token'
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
      write('Failed to submit experiments with SPARK.')
      Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ 
      Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription
      Write-Host "StatusDescription:" $_.Exception.Message
      Exit(-1)
  }
  return $response 
}

$TenantId = '46c98d88-e344-4ed4-8496-4ed7712e255d'
$ClientId = 'b82c0403-5aa9-48bf-9c57-d3deba881d82'

# Get information about all mapped drives
$drives = net use I:
$pg_flag = $false
foreach ($item in $drives) {
	if ($item.contains("Remote name")) {
		if ($item.contains("jf")){
			Write-Host "JF Drive is mapped."
		}
		if ($item.contains("pg")){
			Write-Host "PG Drive is mapped."
			$pg_flag = $true
		}
	}
}

if ($pg_flag){
	Write-Host "Please set the id and password for PG faceless account"
	$UserName = 'enter_pg_faceless_account_username'
	# $tprobot = Get-content -Path "I:\engineering\dev\sctp\users\taipham\taipham.source\sys_tprobot.txt" | ForEach-Object { $_.Trim() }
	$tprobot = 'path to the password for faceless account, the syntax is above. single line and contains password ONLY'
}
else:
	$UserName = 'sys_tprobot@intel.com'
	$tprobot = Get-content -Path "I:\engineering\dev\sctp\users\taipham\taipham.source\sys_tprobot.txt" | ForEach-Object { $_.Trim() }
#$UserName = 'sys_tprobot@intel.com'
# $SCPassword = Read-Host "Password" -AsSecureString
# $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SCPassword)
#$tprobot = Get-content -Path "I:\engineering\dev\sctp\users\taipham\taipham.source\sys_tprobot.txt" | ForEach-Object { $_.Trim() }
$Password = $tprobot
write('Generating SPARK token')
$SparkToken = Get-Token -TenantId $TenantId -ClientId $ClientId -UserName $UserName -Password $Password
write('Generating SPARK token - done')
write('Reading json file')
$Dto = Create-Dto -JsonFilePath $JsonFilePath
write('Reading json file - done')
write('Submiting new experiments with SPARK API')
$SubmissionResult = Submit -SparkToken $SparkToken -Dto $Dto
write('Submiting new experiments with SPARK API- done')
write('Submitted experiment group:')
$SubmissionResult


	  






