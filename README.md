# StegoLLM

A local proxy app for developers using VS Code to interact with LLMs. It compresses prompts using hidden encoding (steganography) to save bandwidth and obscure intent, then decompresses LLM responses seamlessly.

## Features

- Intercepts VS Code ↔ LLM API traffic
- Compresses prompts using steganography (up to 90% reduction)
- Decompresses LLM responses transparently
- Logs compression stats (e.g., token savings)
- Toggle compression on/off
- Web-based settings interface for custom instructions
- Optional deep learning compression
- Compatible with multiple LLM APIs (OpenAI, Claude, Gemini, etc.)

## Why Use StegoLLM?

- **Save on API Costs**: By compressing prompts, you reduce token usage and lower your costs when using paid LLM APIs.
- **Improve Privacy**: Hide sensitive data within compressed prompts for better security in transit.
- **Zero Configuration**: Works with any LLM API without requiring changes to VS Code or the LLM.
- **Customizable Compression**: Create your own compression rules and dictionaries for domain-specific efficiency.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stegollm.git
cd stegollm

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

1. Start the proxy server:

```bash
stegollm start --port 8080
```

2. Configure VS Code to use the proxy:
   - Open VS Code Settings (File > Preferences > Settings)
   - Search for "http.proxy"
   - Set the value to "http://localhost:8080"
   - Restart VS Code

3. Access the web interface at http://localhost:8081

## Advanced Usage

### Command Line Options

```bash
# Start the proxy server with custom ports
stegollm start --port 8080 --ui-port 8081

# Start with verbose logging
stegollm start --verbose

# Use a custom configuration file
stegollm start --config /path/to/config.yaml

# Display version information
stegollm version
```

### Configuration

StegoLLM uses a YAML configuration file located at `~/.config/stegollm/config.yaml` (Linux/macOS) or `%APPDATA%\StegoLLM\config.yaml` (Windows).

Key configuration options:

```yaml
compression:
  enabled: true
  strategy: dictionary  # Options: dictionary, huffman, base2048
  deep_learning_enabled: false

api_compat:
  enabled: true
  supported_apis:
    - openai
    - claude
    - gemini

# More options available...
```

### Custom Instructions

You can create custom compression rules through the web interface or by editing the file at `~/.config/stegollm/custom_instructions.json`:

```json
{
  "rules": [
    {"pattern": "Explain how", "replacement": "EXP:"}
  ],
  "dictionaries": [
    {
      "name": "programming_terms",
      "entries": {
        "function": "fn",
        "variable": "var"
      }
    }
  ]
}
```

## Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific tests
python run_tests.py tests/test_dictionary_strategy.py
```

### Project Structure

- `stegollm/core/`: Core proxy and steganography engine
- `stegollm/strategies/`: Compression strategies
- `stegollm/api_compat/`: API compatibility adapters
- `stegollm/ui/`: Web interface
- `stegollm/config/`: Configuration management
- `tests/`: Test suite

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT