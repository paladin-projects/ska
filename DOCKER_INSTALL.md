<div align="center">

# Docker Installation Guide

Guide for installing Docker on different operating systems

</div>

## Quick Links
- [Linux Installation](#linux)
  - [Ubuntu/Debian](#ubuntudebian)
  - [Arch Linux](#arch-linux)
  - [Fedora](#fedora)
  - [CentOS/RHEL](#centosrhel)
- [Windows Installation](#windows)
- [Troubleshooting](#troubleshooting)

## Linux

### Ubuntu/Debian

```bash
# 1. System preparation
sudo apt update && sudo apt upgrade -y
sudo mkdir -p /etc/apt/keyrings

# 2. Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

# 3. Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

# 4. Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Arch Linux

```bash
# Update system and install Docker
sudo pacman -Syu
sudo pacman -S docker docker-compose
```

### Fedora

```bash
# 1. System preparation
sudo dnf update -y
sudo dnf -y install dnf-plugins-core

# 2. Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# 3. Install Docker
sudo dnf update -y
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### CentOS/RHEL

```bash
# 1. System preparation
sudo yum update -y
sudo yum install -y yum-utils

# 2. Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. Install Docker
sudo yum update -y
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Post-Installation Steps

1. **Start and Enable Docker Service**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Add User to Docker Group**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   systemctl status docker
   ```


## Windows

### Prerequisites
- Windows 10/11 Pro, Enterprise, or Education
- 4GB system RAM
- BIOS-level hardware virtualization support
- WSL 2 and Hyper-V capability

### Installation Steps

1. **Install Docker Desktop**

   **Option 1: Manual Installation**
   - Visit [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Download and run the installer
   - Follow the installation wizard

   **Option 2: PowerShell Installation**
   ```powershell
   # Download and install Docker Desktop
   $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
   $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
   Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath
   Start-Process -Wait $installerPath -ArgumentList "install --quiet"
   Remove-Item $installerPath
   ```

2. **Enable Required Windows Features**
   ```powershell
   # Enable WSL 2
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # Enable Hyper-V
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```

3. **System Restart Required**
   - Restart your computer to apply changes

4. **Verify Installation**
   ```powershell
   docker --version
   docker compose version
   ```

## Troubleshooting

### Common Issues

<details>
<summary>Repository GPG Error</summary>

```bash
# Remove existing keys and lists
sudo rm -f /etc/apt/keyrings/docker.gpg
sudo rm -f /etc/apt/sources.list.d/docker.list

# Re-add repository (Ubuntu example)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" | sudo tee /etc/apt/sources.list.d/docker.list

# Update system
sudo apt update
```
</details>

<details>
<summary>Permission Issues</summary>

```bash
# Check current permissions
ls -l /var/run/docker.sock

# Fix socket permissions
sudo chmod 666 /var/run/docker.sock

# Verify group membership
groups $USER
```
</details>

<details>
<summary>Service Won't Start</summary>

```bash
# Check service status
sudo systemctl status docker

# View logs
sudo journalctl -xu docker

# Restart service
sudo systemctl restart docker
```
</details>

### Additional Resources
- [Official Docker Documentation](https://docs.docker.com/engine/install/)
- [Docker Engine for Linux](https://docs.docker.com/engine/install/linux-postinstall/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)