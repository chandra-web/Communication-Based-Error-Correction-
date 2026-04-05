# modulation_simulator.py
# Digital Modulation Simulator — ASK, FSK, PSK
# Author: Vibha (Nova) | NMIT Bengaluru | ECE

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ──────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────

BITS = [1, 0, 1, 1, 0, 0, 1, 0]   # Input binary message
BIT_RATE = 1                        # 1 bit per second (for clean visuals)
CARRIER_FREQ = 5                    # Hz — carrier frequency (fc)
CARRIER_FREQ_2 = 10                 # Hz — second freq for FSK (f1)
SAMPLE_RATE = 1000                  # Samples per second (resolution)
AMPLITUDE = 1.0                     # Carrier amplitude


# ──────────────────────────────────────────
# TIME AXIS
# ──────────────────────────────────────────

def make_time_axis(bits, bit_rate, sample_rate):
    """Create time axis — one unit per bit."""
    num_samples = int((len(bits) / bit_rate) * sample_rate)
    return np.linspace(0, len(bits) / bit_rate, num_samples)


# ──────────────────────────────────────────
# SIGNAL GENERATORS
# ──────────────────────────────────────────

def generate_carrier(t, frequency, amplitude=1.0):
    """Pure sinusoidal carrier wave: A * sin(2πft)"""
    return amplitude * np.sin(2 * np.pi * frequency * t)


def generate_bit_signal(bits, t, bit_rate):
    """
    Expand bit list into a continuous square wave signal.
    Each bit occupies (1/bit_rate) seconds.
    """
    bit_signal = np.zeros(len(t))
    samples_per_bit = len(t) // len(bits)
    for i, bit in enumerate(bits):
        start = i * samples_per_bit
        end = start + samples_per_bit
        bit_signal[start:end] = bit
    return bit_signal


def modulate_ask(bits, t, bit_rate, fc, amplitude):
    """
    ASK — Amplitude Shift Keying
    ─────────────────────────────
    Bit 1 → carrier ON  (A × sin(2πfct))
    Bit 0 → carrier OFF (0)

    Formula: s(t) = m(t) × A × sin(2πfct)
    where m(t) ∈ {0, 1} is the message signal
    """
    carrier = generate_carrier(t, fc, amplitude)
    bit_signal = generate_bit_signal(bits, t, bit_rate)
    return carrier * bit_signal


def modulate_fsk(bits, t, bit_rate, f0, f1, amplitude):
    """
    FSK — Frequency Shift Keying
    ──────────────────────────────
    Bit 1 → higher frequency f1
    Bit 0 → lower frequency f0

    Formula:
      s(t) = A × sin(2πf1t)  when bit = 1
      s(t) = A × sin(2πf0t)  when bit = 0
    """
    fsk_signal = np.zeros(len(t))
    samples_per_bit = len(t) // len(bits)

    for i, bit in enumerate(bits):
        start = i * samples_per_bit
        end = start + samples_per_bit
        freq = f1 if bit == 1 else f0
        fsk_signal[start:end] = amplitude * np.sin(2 * np.pi * freq * t[start:end])

    return fsk_signal


def modulate_psk(bits, t, bit_rate, fc, amplitude):
    """
    PSK — Phase Shift Keying (BPSK)
    ─────────────────────────────────
    Bit 1 → phase = 0    → A × sin(2πfct)
    Bit 0 → phase = π    → A × sin(2πfct + π) = -A × sin(2πfct)

    Formula: s(t) = A × sin(2πfct + φ(t))
    where φ(t) ∈ {0, π}
    """
    psk_signal = np.zeros(len(t))
    samples_per_bit = len(t) // len(bits)

    for i, bit in enumerate(bits):
        start = i * samples_per_bit
        end = start + samples_per_bit
        phase = 0 if bit == 1 else np.pi
        psk_signal[start:end] = amplitude * np.sin(2 * np.pi * fc * t[start:end] + phase)

    return psk_signal


# ──────────────────────────────────────────
# PLOTTING
# ──────────────────────────────────────────

def plot_all(bits, t, bit_signal, carrier, ask, fsk, psk):
    """Plot all signals in a clean grid layout."""

    fig = plt.figure(figsize=(14, 12))
    fig.patch.set_facecolor('#0e0e12')

    gs = gridspec.GridSpec(6, 1, hspace=0.55)

    plot_configs = [
        (bit_signal,  '#64b5f6', 'Binary Message m(t)',        f'Bits: {bits}'),
        (carrier,     '#aaaaaa', 'Carrier Signal c(t)',         f'fc = {CARRIER_FREQ} Hz'),
        (ask,         '#66bb6a', 'ASK — Amplitude Shift Keying','Bit 1 → ON, Bit 0 → OFF'),
        (fsk,         '#ffa726', 'FSK — Frequency Shift Keying',f'f0={CARRIER_FREQ}Hz (bit 0), f1={CARRIER_FREQ_2}Hz (bit 1)'),
        (psk,         '#ce93d8', 'PSK — Phase Shift Keying',    'Bit 1 → φ=0°, Bit 0 → φ=180°'),
    ]

    axes = []
    for i, (signal, color, title, subtitle) in enumerate(plot_configs):
        ax = fig.add_subplot(gs[i])
        ax.set_facecolor('#16161e')
        ax.plot(t, signal, color=color, linewidth=1.2)
        ax.set_title(f'{title}', color='white', fontsize=11, fontweight='bold', pad=6)
        ax.set_ylabel(subtitle, color='#888', fontsize=8, labelpad=4)
        ax.tick_params(colors='#555')
        for spine in ax.spines.values():
            spine.set_color('#2a2a3a')
        ax.set_xlim(t[0], t[-1])
        ax.axhline(0, color='#333', linewidth=0.5)

        # Draw bit boundaries
        for b in range(len(bits) + 1):
            ax.axvline(b / BIT_RATE, color='#333', linewidth=0.6, linestyle='--')

        # Label bits on top of message signal
        if i == 0:
            for b_idx, bit in enumerate(bits):
                ax.text(b_idx + 0.5, 0.6, str(bit),
                        color='white', fontsize=10, ha='center', fontweight='bold')

        axes.append(ax)

    # Add BER info box
    ax_info = fig.add_subplot(gs[5])
    ax_info.set_facecolor('#0e0e12')
    ax_info.axis('off')
    info_text = (
        "📡  MODULATION SUMMARY\n\n"
        f"  ASK  →  Varies AMPLITUDE  |  Simple, susceptible to noise  |  Used in optical comms\n"
        f"  FSK  →  Varies FREQUENCY  |  More noise-resistant than ASK  |  Used in Bluetooth, caller ID\n"
        f"  PSK  →  Varies PHASE      |  Most bandwidth-efficient       |  Used in WiFi (802.11), satellite comms"
    )
    ax_info.text(0.01, 0.5, info_text, color='#94a3b8', fontsize=9,
                 va='center', fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e1e2a', edgecolor='#2a2a3a'))

    # Title
    fig.suptitle('Digital Modulation Simulator — ASK | FSK | PSK',
                 color='white', fontsize=14, fontweight='bold', y=0.98)

    plt.savefig('modulation_output.png', dpi=150, bbox_inches='tight',
                facecolor='#0e0e12')
    print("✅  Plot saved → modulation_output.png")
    plt.show()


# ──────────────────────────────────────────
# METRICS
# ──────────────────────────────────────────

def compute_metrics(ask, fsk, psk, carrier):
    """Basic signal metrics for each modulated signal."""
    print("\n📊  Signal Metrics")
    print("─" * 40)
    for name, signal in [("ASK", ask), ("FSK", fsk), ("PSK", psk)]:
        power = np.mean(signal ** 2)
        peak  = np.max(np.abs(signal))
        print(f"  {name}  |  Power: {power:.4f} W  |  Peak: {peak:.4f} V")
    print("─" * 40)


# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Digital Modulation Simulator")
    print("  ASK | FSK | PSK")
    print("=" * 50)
    print(f"\n  Input bits   : {BITS}")
    print(f"  Carrier freq : {CARRIER_FREQ} Hz")
    print(f"  FSK f0 / f1  : {CARRIER_FREQ} Hz / {CARRIER_FREQ_2} Hz")
    print(f"  Sample rate  : {SAMPLE_RATE} Hz\n")

    # Build time axis
    t = make_time_axis(BITS, BIT_RATE, SAMPLE_RATE)

    # Generate all signals
    bit_signal = generate_bit_signal(BITS, t, BIT_RATE)
    carrier    = generate_carrier(t, CARRIER_FREQ, AMPLITUDE)
    ask        = modulate_ask(BITS, t, BIT_RATE, CARRIER_FREQ, AMPLITUDE)
    fsk        = modulate_fsk(BITS, t, BIT_RATE, CARRIER_FREQ, CARRIER_FREQ_2, AMPLITUDE)
    psk        = modulate_psk(BITS, t, BIT_RATE, CARRIER_FREQ, AMPLITUDE)

    # Metrics
    compute_metrics(ask, fsk, psk, carrier)

    # Plot
    plot_all(BITS, t, bit_signal, carrier, ask, fsk, psk)


if __name__ == "__main__":
    main()