# Triggered by autounattend.xml's FirstLogonCommands. Runs once at first
# logon under the bootstrap 'user' account with full admin rights.
# Per C-9: enable WinRM HTTP listener so Packer's communicator connects.
# OpenSSH server installation moves to a Packer powershell provisioner.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Win11 24H2 — bypass Microsoft account requirement on OOBE.
if ([System.Environment]::OSVersion.Version.Build -ge 22000) {
  New-Item -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE' -Force | Out-Null
  New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE' `
    -Name BypassNRO -Value 1 -PropertyType DWord -Force | Out-Null
}

# WinRM listener on TCP/5985 (HTTP). Build-time only; sysprep generalize
# disables it so clones never expose WinRM.
winrm quickconfig -quiet
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
Enable-PSRemoting -Force

# Open TCP/5985 on Public + Private + Domain firewall profiles. Build VM
# adapter is on the homelab LAN which Windows may classify as Public until
# network identification completes; covering all three avoids races.
New-NetFirewallRule -Name 'WinRM-HTTP' -DisplayName 'WinRM (HTTP 5985)' `
  -Protocol TCP -LocalPort 5985 -Action Allow -Direction Inbound `
  -Profile Public,Private,Domain | Out-Null

# Persist autounattend.xml so sysprep /generalize re-runs specialize/oobe
# cleanly on first clone boot (per C-8 design note about C:\Windows\Panther\unattend.xml).
Copy-Item -Path 'A:\autounattend.xml' -Destination 'C:\Windows\Panther\unattend.xml' -Force -ErrorAction SilentlyContinue
