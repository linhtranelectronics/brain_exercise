# import sys
# import time
# import re
# import json

# try:
#     import serial
#     from serial.serialutil import SerialException
# except ImportError:
#     print("Missing dependency 'pyserial'. Install with: pip install pyserial")
#     sys.exit(1)

# PORT = 'COM3'
# BAUDRATE = 115200
# poor = -1
# attention =-1
# meditation = -1
# blink = -1
# def open_serial(port, baudrate, timeout=1):
#     try:
#         ser = serial.Serial(port, baudrate, timeout=timeout)
#         return ser
#     except SerialException as e:
#         print(f"Failed to open serial port {port}: {e}")
#         return None


# def _norm_name(name: str) -> str:
#     """Normalize a key name to one of: poor, attention, meditation, blink"""
#     if not name:
#         return name
#     n = name.lower()
#     # common variants
#     if 'poor' in n or 'poor' in n or 'signal' in n:
#         return 'poor'
#     if 'att' in n:
#         return 'attention'
#     if 'med' in n:
#         return 'meditation'
#     if 'blink' in n:
#         return 'blink'
#     return n


# def parse_line(line: str):

#     out = {}
#     s = line.strip()
#     if not s:
#         return out



#     # If contains key:value pairs like "PoorSignal:0, Attention:45"
#     if ':' in s or '=' in s:
#         parts = re.split(r'[;,]', s)
#         for p in parts:
#             if not p.strip():
#                 continue
#             if ':' in p:
#                 name, val = p.split(':', 1)
#             elif '=' in p:
#                 name, val = p.split('=', 1)
#             else:
#                 continue
#             key = _norm_name(name.strip())
#             val = val.strip()
#             if key:
#                 try:
#                     out[key] = int(val)
#                 except Exception:
#                     try:
#                         out[key] = float(val)
#                     except Exception:
#                         out[key] = val
#         return out

#     # Otherwise try CSV numbers
#     parts = [p.strip() for p in s.split(',') if p.strip()]
#     if len(parts) >= 3:
#         # assume order: PoorSignal, attention, meditation, blink (blink optional)
#         names = ['poor', 'attention', 'meditation', 'blink']
#         for i, val in enumerate(parts[:4]):
#             key = names[i]
#             try:
#                 out[key] = int(val)
#             except Exception:
#                 try:
#                     out[key] = float(val)
#                 except Exception:
#                     out[key] = val
#         return out

#     # Last resort: try to extract numbers in order from the line
#     nums = re.findall(r'-?\d+', s)
#     if nums:
#         names = ['poor', 'attention', 'meditation', 'blink']
#         for i, n in enumerate(nums[:4]):
#             out[names[i]] = int(n)
#     return out


# def read_loop(ser):
#     print(f"Listening on {ser.port} @ {ser.baudrate} baud. Press Ctrl+C to exit.")
#     try:
#         while True:
#             try:
#                 print("reading...")
#                 line = ser.readline()
#                 print(f"reading...{line}")
#             except SerialException as e:
#                 print(f"Serial error while reading: {e}")
#                 break
#             if not line:
#                 time.sleep(0.01)
#                 print("no data")
#                 continue
#             try:
#                 text = line.decode('utf-8', errors='replace')
#             except Exception:
#                 text = line.decode('latin-1', errors='replace')

#             text = text.rstrip('\r\n')
#             print(f"Received: {text}")
#             data = parse_line(text)
#             # Map parsed values into variables with defaults
#             poor = data.get('poor')
#             attention = data.get('attention')
#             meditation = data.get('meditation')
#             blink = data.get('blink')

#             # Print a concise line showing the parsed values
#             if data:
#                 print(f"PoorSignal={poor}  Attention={attention}  Meditation={meditation}  Blink={blink}")
#             else:
#                 # if parsing failed, print raw text for debugging
#                 print(f"(raw) {text}")
#     except KeyboardInterrupt:
#         print('\nUser requested exit')

# def runSerial():
#     ser = open_serial(PORT, BAUDRATE)
#     if ser is None:
#         print('Exiting.')
#         sys.exit(1)
#     try:
#         read_loop(ser)
#     finally:
#         try:
#             ser.close()
#         except Exception:
#             pass
# runSerial()
# print("Module ReadSerial loaded.")
import serial
import time

# Serial port configuration
# 1. Replace 'COMx' with the name of your Arduino's Serial port
#    (e.g., 'COM3' on Windows, '/dev/ttyACM0' or '/dev/ttyUSB0' on Linux/Mac)
# 2. Baud rate must match the Arduino code (9600)
SERIAL_PORT = 'COM4'  # <<< CHANGE YOUR PORT NAME HERE
BAUD_RATE = 115200

# Names of the parameters sent from Arduino
PARAM_NAMES = ['poor', 'attention', 'meditation', 'blink']

def read_serial_data():
    try:
        # Initialize Serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(1)  # Wait 2 seconds for the Serial connection to stabilize
        print(f"Connection established on port {SERIAL_PORT} at {BAUD_RATE} baud.")
        print("-" * 35)

        while True:
            # Read a line of data (terminated by '\n' sent by Serial.println())
            if ser.in_waiting > 0:
                # Read bytes, decode to string, and remove newline characters ('\r\n')
                line = ser.readline().decode('utf-8').strip()

                if line:
                    try:
                        # Split the string by comma
                        values = line.split(',')

                        # Ensure there are exactly 4 values
                        if len(values) == 4:
                            # Convert string values to integers
                            data = [int(v) for v in values]

                            # Print to screen in a clear format
                            print(f"Poor: {data[0]:<3} | Attention: {data[1]:<3} | Meditation: {data[2]:<3} | Blink: {data[3]}")

                        else:
                            print(f"Data error: {line} (Expected 4 values)")

                    except ValueError:
                        # Catch error if values are not integers
                        print(f"Value conversion error: {line}")
                    
                # Wait briefly to avoid high CPU load
                time.sleep(0.01)

    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print(f"Please check port '{SERIAL_PORT}' and ensure Arduino is connected and the port is free.")
    except KeyboardInterrupt:
        print("\nPython program stopped.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")