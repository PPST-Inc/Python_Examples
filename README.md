# SCPI Communication Examples

Collection of Python examples using SCPI (Standard Commands for Programmable Instruments) protocol via TCP/IP and VISA.

## Available Examples

### Prerequisites

- **Python 3.6+** installed
- For VISA examples: `pyvisa` and `pyvisa-py` packages (auto-installed by script)

### Installation

Python examples work on Windows, Linux (Ubuntu), and macOS.

```bash
# No installation needed for TCP/IP examples
# VISA examples auto-install dependencies on first run

# Or install manually:
pip install pyvisa pyvisa-py
```

### Usage

#### 1. Basic Configuration Example (TCP/IP)
Configures a power source to AC mode, 100V, 60Hz and enables output.

```bash
# Default IP
python python_basic_configuration_example.py

# Custom IP
python python_basic_configuration_example.py --ip 192.168.1.100

# Custom port
python python_basic_configuration_example.py --port 5025
```

#### 2. Interactive SCPI Commands (TCP/IP)
Opens an interactive terminal to send SCPI commands manually.

```bash
python python_scpi_command_example.py --ip 192.168.131.193

# In the terminal:
SCPI> *IDN?
SCPI> VOLT:AC 100
SCPI> FREQ 60
SCPI> OUTP 1
SCPI> exit
```

#### 3. SCPI Commands via VISA
Communicates using VISA protocol (supports TCPIP, GPIB, USB, Serial).

```bash
# Connect via TCP/IP
python python_scpi_command_by_visa_example.py --resource "TCPIP0::192.168.1.100::inst0::INSTR"

# Connect via GPIB
python python_scpi_command_by_visa_example.py --resource "GPIB0::10::INSTR"

```

**VISA Resource String Formats:**
- **TCPIP:** `TCPIP0::<ip_address>::inst0::INSTR`
- **GPIB:** `GPIB0::<address>::INSTR`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pyvisa'"
```bash
pip install pyvisa pyvisa-py
```

### "Connection timeout"
- Verify equipment IP address
- Check network connectivity
- Disable firewall temporarily
- Ensure equipment is on same subnet

### Ubuntu: "pip install failed"
```bash
sudo apt update
sudo apt install python3-pip
pip3 install pyvisa pyvisa-py
```
