$f = 'C:\Users\yrakotch\source\repos\nvl_cpu_idg\.tmp_rzl_ver5\FUN_CORE_CXPKGS9_expected_V5.mtpl'
$names = @(
  'SBFT_CORE_VMIN_K_F5XCR_X_CR_',
  'SBFT_CORE_VMIN_K_F1XCR_X_CR_F1_',
  'SBFT_CORE_VMIN_K_F2XCR_X_CR_F2_',
  'SBFT_CORE_VMIN_K_F3XCR_X_CR_F3_',
  'SBFT_CORE_VMIN_K_F4XCR_X_CR_F4_',
  'SBFT_CORE_VMIN_K_FMINXCR_X_CR_FMIN_',
  'SBFT_CORE_VMAX_K_C5VMAXXCR_X_CR_',
  'SBFT_CORE_VMAX_K_VMAXXCR_X_CR_',
  'SBFT_CORE_VMIN_K_VMAXXCR_X_CR_F1_X_MLC_LS',
  'SBFT_CORE_VMIN_K_VMAXXCR_X_CR_F1_X_',
  'FUN_CORE_CXPKGS9_INIT',
  'FUN_CORE_CXPKGS9_F5XCR',
  'FUN_CORE_CXPKGS9_F1XCR',
  'FUN_CORE_CXPKGS9_F2XCR',
  'FUN_CORE_CXPKGS9_F3XCR',
  'FUN_CORE_CXPKGS9_F4XCR',
  'FUN_CORE_CXPKGS9_FMINXCR',
  'FUN_CORE_CXPKGS9_VMAXXCR'
)
foreach ($n in $names) {
  $hits = Select-String -Path $f -SimpleMatch -Pattern $n
  $count = $hits.Count
  $sample = ($hits | Select-Object -First 2 | ForEach-Object { "L$($_.LineNumber): $($_.Line.Trim())" }) -join '  ||  '
  '{0,-45} refs={1,3}  {2}' -f $n, $count, $sample
}
