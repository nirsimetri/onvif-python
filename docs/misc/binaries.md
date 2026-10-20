---
hide:
  - path
comments: true
---

# Prebuilt Binaries (No Python Required)

Run the [ONVIF CLI](../main/onvif_cli.md) without installing Python or additional dependencies. Download a prebuilt binary for your platform from the [GitHub Releases](https://github.com/nirsimetri/onvif-python/releases) page.

Each release provides ZIP archives for supported operating systems and architectures. Choose the appropriate binary from the table below.

| Platform | Architecture | Download |
|---|---|---|
| :fontawesome-brands-linux: &nbsp;Linux | AMD64 (64-bit) | [onvif-linux-amd64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-amd64.zip) |
| :fontawesome-brands-linux: &nbsp;Linux | i386 (32-bit) | [onvif-linux-i386.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-i386.zip) |
| :fontawesome-brands-linux: &nbsp;Linux | ARM64 (aarch64) | [onvif-linux-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-arm64.zip) |
| :fontawesome-brands-windows: &nbsp;Windows | x64 (64-bit) | [onvif-windows-win64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-win64.zip) |
| :fontawesome-brands-windows: &nbsp;Windows | x86 (32-bit) | [onvif-windows-win32.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-win32.zip) |
| :fontawesome-brands-windows: &nbsp;Windows | ARM64 | [onvif-windows-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-arm64.zip) |
| :fontawesome-brands-apple: &nbsp;macOS | Intel (AMD64) | [onvif-macos-amd64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-macos-amd64.zip) |
| :fontawesome-brands-apple: &nbsp;macOS | Apple Silicon (ARM64) | [onvif-macos-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-macos-arm64.zip) |

## Installation

### :fontawesome-brands-linux: Linux

1. Download the ZIP archive matching your Linux architecture.
2. Extract the archive into a permanent location.
3. Create a symbolic link in `~/.local/bin` so the executable can be invoked from any directory.

For example, for Linux AMD64, assuming the archive is in `~/Downloads`:

```console
mkdir -p ~/.local/opt ~/.local/bin
unzip ~/Downloads/onvif-linux-amd64.zip -d ~/.local/opt
chmod +x ~/.local/opt/onvif/onvif
ln -sf ~/.local/opt/onvif/onvif ~/.local/bin/onvif
```

Ensure `~/.local/bin` is included in your `PATH`. If necessary, add the following to `~/.bashrc` or `~/.zshrc`:

```console
export PATH="$HOME/.local/bin:$PATH"
```

Reload your shell configuration or open a new terminal, then verify:

```console
onvif --help
```

Replace `onvif-linux-amd64.zip` with the archive matching your system.

### :fontawesome-brands-windows: Windows

1. Download the ZIP archive matching your Windows architecture.
2. Extract the archive. It contains an `onvif` directory with the executable and its bundled dependencies.
3. Move the extracted `onvif` directory to a permanent location, such as `%LOCALAPPDATA%\Programs\ONVIF`.
4. Add that directory to your user `PATH` environment variable.

To configure `PATH`, open **Edit environment variables for your account**, select `Path`, click **New**, and enter:

```text
%LOCALAPPDATA%\Programs\ONVIF
```

Open a new terminal and verify the installation:

```console
onvif --help
```

You can now invoke `onvif` from any working directory in PowerShell or Command Prompt.

### :fontawesome-brands-apple: macOS

1. Download the ZIP archive matching your Mac's processor: Intel or Apple Silicon.
2. Extract the archive into a permanent location.
3. Create a symbolic link in `~/.local/bin`.

For example, for Apple Silicon:

```console
mkdir -p ~/.local/opt ~/.local/bin
unzip ~/Downloads/onvif-macos-arm64.zip -d ~/.local/opt
chmod +x ~/.local/opt/onvif/onvif
ln -sf ~/.local/opt/onvif/onvif ~/.local/bin/onvif
```

Ensure `~/.local/bin` is included in your `PATH`. If necessary, add this line to `~/.zshrc`:

```console
export PATH="$HOME/.local/bin:$PATH"
```

Open a new terminal and verify:

```console
onvif --help
```

For Intel Macs, use `onvif-macos-amd64.zip` instead.

## Understanding the Distribution

The prebuilt binaries use PyInstaller's `--onedir` mode. Each archive contains the executable, bundled runtime dependencies, and project license documents.

The extracted directory has the following structure:

```text
onvif/
├── onvif          # Linux and macOS
├── onvif.exe      # Windows only
├── LICENSE
├── NOTICE
└── _internal/
    └── ...        # Bundled runtime and dependencies
```

The `_internal` directory contains the Python runtime components, third-party dependencies, and bundled resources required by the executable.

**Keep the executable and `_internal` directory together.** Do not delete, rename, or move `_internal` independently. The application may fail to start or operate correctly if its bundled files are missing.

The `LICENSE` and `NOTICE` files provide licensing and attribution information for the distribution.

## Verify the Installation

After completing the platform-specific setup, run:

```console
onvif --help
```

To see the available commands and options, consult the [ONVIF CLI documentation](../main/onvif_cli.md).

These prebuilt binaries do not require a separate Python installation or a separate installation of the ONVIF Python package.
