# StegoLLM Installation Guide

This guide provides step-by-step instructions for installing and setting up StegoLLM, a local proxy application that compresses LLM prompts to save API costs and improve privacy.

## Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation Methods

### Method 1: Standard Installation

1. Clone the repository (or download and extract the zip file):
   ```bash
   git clone https://github.com/yourusername/stegollm.git
   cd stegollm
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

### Method 2: Using Docker

If you prefer using Docker, we provide a Dockerfile and docker-compose.yml:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stegollm.git
   cd stegollm
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Configuration

StegoLLM uses a YAML configuration file located at:

- Linux/macOS: `~/.config/stegollm/config.yaml`
- Windows: `%APPDATA%\StegoLLM\config.yaml`

A default configuration file will be created on first run if one doesn't exist.

### Custom Configuration

You can create a custom configuration file and specify it with the `--config` option:

```bash
stegollm start --config /path/to/your/config.yaml
```

## Setting Up VS Code

To use StegoLLM with VS Code:

1. Open VS Code Settings (File > Preferences > Settings)
2. Search for "http.proxy"
3. Set the value to "http://localhost:8080" (or the port you configured)
4. Restart VS Code

## Running StegoLLM

### Command Line

Start the proxy server:

```bash
stegollm start
```

With custom options:

```bash
stegollm start --port 8080 --ui-port 8081 --verbose
```

### Web Interface

Once StegoLLM is running, you can access the web interface at:

```
http://localhost:8081
```

The web interface allows you to:
- Monitor compression statistics
- Configure settings
- Create custom compression rules
- View logs and performance metrics

## Verifying Installation

1. Start the proxy server
2. Visit http://localhost:8081 in your web browser
3. Confirm that you see the StegoLLM dashboard
4. Make a request from VS Code to an LLM API and check that it's being compressed

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 8080 or 8081 are already in use, specify different ports:
   ```bash
   stegollm start --port 8888 --ui-port 8889
   ```

2. **VS Code not using proxy**: Ensure VS Code settings have been updated and VS Code has been restarted.

3. **Permission issues**: If you encounter permission errors, try:
   ```bash
   pip install --user -e .
   ```

4. **TLS errors**: If you encounter TLS errors, try disabling TLS termination in the configuration or setting up certificates.

### Getting Help

If you encounter issues, check the logs:

```bash
cat ~/.config/stegollm/logs/stegollm.log
```

## Updating StegoLLM

To update to the latest version:

```bash
git pull
pip install -e .
```

Or with Docker:

```bash
docker-compose pull
docker-compose up -d --build