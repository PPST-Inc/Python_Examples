# PPST - SCPI commands via TCP/IP
# Version: 1.0.0
# Date: 12/03/2025

import socket
import sys
import argparse

# Default configuration
DEFAULT_IP = "192.168.131.193"
DEFAULT_PORT = 5025             # Standard SCPI port
CONNECTION_TIMEOUT = 5          # Timeout in seconds

# Helper function to wait for user input before closing the script
def wait_for_key_press(message="\nPress ENTER to close..."):
    try:
        input(message)
    except:
        pass

# Class for communication with SCPI Unit via TCP/IP
# - ip (str): Unit IP address
# - port (int): TCP port (default: 5025)
# - timeout (int): Connection timeout in seconds
class SocketConnection:
    def __init__(self, ip, port=DEFAULT_PORT, timeout=CONNECTION_TIMEOUT):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = None

    # Establish connection with the Unit
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.port))
            print(f"✓ Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    # Send an SCPI command to the Unit
    # - command (str): SCPI command to send
    def send_command(self, command):
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.sendall(command.encode())
            print(f"→ Sent: {command.strip()}")
        except Exception as e:
            print(f"✗ Error sending command: {e}")

    # Send a query command and receive response
    # - command (str): SCPI query command
    # Returns: str: Unit response
    def query(self, command):
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.sendall(command.encode())
            print(f"→ Query: {command.strip()}")
            response = self.socket.recv(65535).decode().strip()
            print(f"← Response: {response}")
            return response
        except Exception as e:
            print(f"✗ Query error: {e}")
            return None

    # Close connection with the Unit
    def disconnect(self):
        if self.socket:
            self.socket.close()
            print(f"✓ Disconnected from {self.ip}")

def scpi_command(socket):
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
                socket.query(command)
            else:
                socket.send_command(command)

        except KeyboardInterrupt:
            print("\n✓ Exiting...")
            break
        except Exception as e:
            print(f"✗ Error: {e}")


# Main script function
def main():
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description='Configuration of laboratory equipment using SCPI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Usage examples:
            python script.py --ip 192.168.1.100       # Specify different IP
            python script.py --port 5025              # Specify different port
        """
    )
    parser.add_argument('--ip', type=str, default=DEFAULT_IP, help=f'Instrument IP address (default: {DEFAULT_IP})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'TCP port (default: {DEFAULT_PORT})')
    args = parser.parse_args()

    # Display connection information
    print("============================================================")
    print("SCPI COMMANDS - TCP/IP COMMUNICATION")
    print("============================================================")
    print(f"IP: {args.ip}")
    print(f"Port: {args.port}")
    print("============================================================")

    # Create socket object and connect
    socket = SocketConnection(args.ip, args.port)

    if not socket.connect():
        print("\n✗ Could not establish connection. Verify:")
        print("  - The equipment is powered on")
        print("  - The IP address is correct")
        print("  - The equipment is on the same network")
        print("  - The firewall allows the connection")
        wait_for_key_press("\nPress ENTER to close...")
        sys.exit(1)

    try:
        scpi_command(socket)
    except KeyboardInterrupt:
        print("\n\n✓ Program interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        wait_for_key_press("\nPress ENTER to close...")
    finally:
        # Always disconnect at the end
        socket.disconnect()
        print("\n✓ Program finished")
        wait_for_key_press()

if __name__ == "__main__":
    main()