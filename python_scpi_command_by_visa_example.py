# PPST - SCPI commands via VISA
# Version: 1.0.0
# Date: 12/03/2025

import sys
import argparse
import subprocess

# Auto-install pyvisa and pyvisa-py if not available
def install_dependencies():
    """Check and install required packages"""
    required_packages = ['pyvisa', 'pyvisa-py']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Missing packages detected: {', '.join(missing_packages)}")
        print("Attempting automatic installation...\n")

        try:
            # Try installation with suppressed output
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--user'] + missing_packages,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✓ Packages installed successfully\n")
                # Verify installation worked
                for package in missing_packages:
                    try:
                        __import__(package.replace('-', '_'))
                    except ImportError:
                        print(f"✗ Installation succeeded but package {package} still not found")
                        print("Try restarting the script or install manually")
                        sys.exit(1)
            else:
                print(f"✗ Installation failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error details: {result.stderr[:500]}")
                raise Exception("pip install failed")
                
        except Exception as e:
            print(f"\n✗ Automatic installation failed: {e}")
            print("\nPlease install manually using one of these methods:")
            print(f"  • pip install pyvisa pyvisa-py")
            print(f"  • pip3 install pyvisa pyvisa-py")
            print(f"  • python3 -m pip install pyvisa pyvisa-py")
            print(f"  • sudo apt install python3-pip && pip3 install pyvisa pyvisa-py")
            sys.exit(1)

# Install dependencies before importing pyvisa
install_dependencies()

import pyvisa

# Default configuration
DEFAULT_RESOURCE = "TCPIP0::192.168.123.1::inst0::INSTR"
CONNECTION_TIMEOUT = 5000  # Timeout in milliseconds

# Helper function to wait for user input before closing the script
def wait_for_key_press(message="\nPress ENTER to close..."):
    try:
        input(message)
    except:
        pass

# Class for communication with SCPI Unit via VISA
# - resource_string (str): VISA resource string (e.g., "TCPIP0::192.168.1.1::inst0::INSTR")
# - timeout (int): Connection timeout in milliseconds
class VISAConnection:
    def __init__(self, resource_string, timeout=CONNECTION_TIMEOUT):
        self.resource_string = resource_string
        self.timeout = timeout
        self.instrument = None
        self.rm = None

    # Establish connection with the Unit
    def connect(self):
        try:
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(self.resource_string)
            self.instrument.timeout = self.timeout
            print(f"✓ Connected to {self.resource_string}")
            return True
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    # Send an SCPI command to the Unit
    # - command (str): SCPI command to send
    def send_command(self, command):
        try:
            self.instrument.write(command)
            print(f"→ Sent: {command.strip()}")
        except Exception as e:
            print(f"✗ Error sending command: {e}")

    # Send a query command and receive response
    # - command (str): SCPI query command
    # Returns: str: Unit response
    def query(self, command):
        try:
            response = self.instrument.query(command).strip()
            print(f"→ Query: {command.strip()}")
            print(f"← Response: {response}")
            return response
        except Exception as e:
            print(f"✗ Query error: {e}")
            return None

    # Close connection with the Unit
    def disconnect(self):
        if self.instrument:
            self.instrument.close()
            print(f"✓ Disconnected from {self.resource_string}")
        if self.rm:
            self.rm.close()

def scpi_command(visa_conn):
    print("\nEnter SCPI commands directly. Type 'exit' to quit.")
    print("Use '?' at the end of the command to make a query.\n")
    
    while True:
        try:
            command = input("SCPI> ").strip()
            if command.lower() in ['exit', 'quit']:
                break

            if not command:
                continue

            # If the command ends in '?', it's a query
            if command.endswith('?'):
                visa_conn.query(command)
            else:
                visa_conn.send_command(command)

        except KeyboardInterrupt:
            print("\n✓ Exiting...")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

# Main script function
def main():
    
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description='Configuration using SCPI via VISA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python scpi_visa_example.py
  python scpi_visa_example.py --resource "TCPIP0::192.168.1.100::inst0::INSTR"
  python scpi_visa_example.py --resource "GPIB0::10::INSTR"
  
Common VISA resource string formats:
  TCPIP: TCPIP0::<ip_address>::inst0::INSTR
  GPIB:  GPIB0::<address>::INSTR
        """
    )
    parser.add_argument('--resource', type=str, default=DEFAULT_RESOURCE, 
                        help=f'VISA resource string (default: {DEFAULT_RESOURCE})')
    parser.add_argument('--timeout', type=int, default=CONNECTION_TIMEOUT,
                        help=f'Connection timeout in milliseconds (default: {CONNECTION_TIMEOUT})')
    args = parser.parse_args()

    # Display connection information
    print("============================================================")
    print("SCPI COMMANDS - VISA COMMUNICATION")
    print("============================================================")
    print(f"Resource: {args.resource}")
    print(f"Timeout: {args.timeout} ms")
    print("============================================================")

    # Create VISA connection object and connect
    visa_conn = VISAConnection(args.resource, args.timeout)

    if not visa_conn.connect():
        print("\n✗ Could not establish connection. Verify:")
        print("  - PyVISA and VISA backend are properly installed")
        print("  - The equipment is powered on")
        print("  - The resource string is correct")
        print("  - The equipment is accessible via VISA")
        wait_for_key_press()
        sys.exit(1)

    try:
        # Query instrument identification
        print("\nQuerying instrument identification...")
        idn = visa_conn.query("*IDN?")

        # Start interactive command mode
        scpi_command(visa_conn)
        
    except KeyboardInterrupt:
        print("\n\n✓ Program interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        wait_for_key_press()
    finally:
        # Always disconnect at the end
        visa_conn.disconnect()
        print("\n✓ Program finished")
        wait_for_key_press()

if __name__ == "__main__":
    main()
