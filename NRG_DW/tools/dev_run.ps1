$env:JAVA_HOME="C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot"; $env:PENTAHO_JAVA_HOME=$env:JAVA_HOME; $env:PATH="$env:JAVA_HOME\bin;$env:PATH"; $env:KETTLE_HOME="C:\pdi\kettle_home"
python NRG_DW\tools\gen_pdi.py | Out-Null
cmd /c "C:\pdi\data-integration\Kitchen.bat /file:NRG_DW\pentaho\J_NRG_DW_Main.kjb /level:Basic > NRG_DW\run1.log 2>&1"
Select-String -Path NRG_DW\run1.log -Pattern "ERROR|Finished job entry|Caused|Finished processing|Kitchen -" | select -First 40 | % { $_.Line.Substring(0,[Math]::Min(330,$_.Line.Length)) }
