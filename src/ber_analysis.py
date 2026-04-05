# ber_analysis.py
# BER vs SNR Analysis for ASK, FSK, PSK
# Bit Error Rate — how each modulation handles noise
# Author: Vibha (Nova) | NMIT Bengaluru | ECE

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc   # complementary error function


# ──────────────────────────────────────────
# THEORETICAL BER FORMULAS
# ──────────────────────────────────────────
# These are the actual formulas from your
# Communication Systems textbook (Haykin / Lathi)
# ──────────────────────────────────────────

def ber_ask_theoretical(snr_linear):
    """
    BER for coherent ASK (OOK):
    Pe = 0.5 × erfc( sqrt(SNR/4) )
    """
    return 0.5 * erfc(np.sqrt(snr_linear / 4))


def ber_fsk_theoretical(snr_linear):
    """
    BER for coherent FSK:
    Pe = 0.5 × erfc( sqrt(SNR/2) )
    FSK is better than ASK by 3 dB
    """
    return 0.5 * erfc(np.sqrt(snr_linear / 2))


def ber_psk_theoretical(snr_linear):
    """
    BER for BPSK:
    Pe = 0.5 × erfc( sqrt(SNR) )
    BPSK is the most efficient — best BER for same SNR
    """
    return 0.5 * erfc(np.sqrt(snr_linear))


# ──────────────────────────────────────────
# SIMULATED BER (Monte Carlo)
# ──────────────────────────────────────────

def simulate_ber(modulation, snr_db_range, num_bits=10000):
    """
    Monte Carlo BER simulation.
    Generate random bits → modulate → add AWGN noise →
    demodulate → count errors.
    """
    ber_simulated = []

    for snr_db in snr_db_range:
        snr_linear = 10 ** (snr_db / 10)
        noise_std = 1 / np.sqrt(2 * snr_linear)

        bits = np.random.randint(0, 2, num_bits)
        errors = 0

        for bit in bits:
            # Simple symbol model: +1 for bit 1, -1 (or 0) for bit 0
            if modulation == "PSK":
                symbol = 1.0 if bit == 1 else -1.0
                received = symbol + np.random.normal(0, noise_std)
                detected = 1 if received > 0 else 0

            elif modulation == "ASK":
                symbol = 1.0 if bit == 1 else 0.0
                received = symbol + np.random.normal(0, noise_std)
                detected = 1 if received > 0.5 else 0

            elif modulation == "FSK":
                # FSK: correlate with two frequencies
                # Simplified: treat as two orthogonal symbols
                symbol = 1.0 if bit == 1 else -1.0
                received = symbol + np.random.normal(0, noise_std * np.sqrt(2))
                detected = 1 if received > 0 else 0

            if detected != bit:
                errors += 1

        ber_simulated.append(errors / num_bits)

    return np.array(ber_simulated)


# ──────────────────────────────────────────
# PLOT
# ──────────────────────────────────────────

def plot_ber(snr_db_range):
    snr_linear = 10 ** (snr_db_range / 10)

    # Theoretical curves
    ber_ask_th  = ber_ask_theoretical(snr_linear)
    ber_fsk_th  = ber_fsk_theoretical(snr_linear)
    ber_psk_th  = ber_psk_theoretical(snr_linear)

    # Simulated points (fewer points for speed)
    snr_sim = np.arange(0, 16, 2)
    ber_ask_sim = simulate_ber("ASK", snr_sim)
    ber_fsk_sim = simulate_ber("FSK", snr_sim)
    ber_psk_sim = simulate_ber("PSK", snr_sim)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#0e0e12')
    ax.set_facecolor('#16161e')

    # Theoretical lines
    ax.semilogy(snr_db_range, ber_ask_th,  color='#66bb6a', linewidth=2,   label='ASK — Theoretical')
    ax.semilogy(snr_db_range, ber_fsk_th,  color='#ffa726', linewidth=2,   label='FSK — Theoretical')
    ax.semilogy(snr_db_range, ber_psk_th,  color='#ce93d8', linewidth=2,   label='PSK — Theoretical')

    # Simulated dots
    ax.semilogy(snr_sim, ber_ask_sim, 'o', color='#66bb6a', markersize=7,  label='ASK — Simulated')
    ax.semilogy(snr_sim, ber_fsk_sim, 's', color='#ffa726', markersize=7,  label='FSK — Simulated')
    ax.semilogy(snr_sim, ber_psk_sim, '^', color='#ce93d8', markersize=7,  label='PSK — Simulated')

    ax.set_xlabel('SNR (dB)', color='#94a3b8', fontsize=12)
    ax.set_ylabel('Bit Error Rate (BER)', color='#94a3b8', fontsize=12)
    ax.set_title('BER vs SNR — ASK | FSK | PSK\n(Theoretical + Monte Carlo Simulation)',
                 color='white', fontsize=13, fontweight='bold')

    ax.tick_params(colors='#555')
    ax.grid(True, which='both', color='#2a2a3a', linestyle='--', linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_color('#2a2a3a')

    legend = ax.legend(facecolor='#1e1e2a', edgecolor='#2a2a3a',
                       labelcolor='white', fontsize=10)

    # Annotation
    ax.annotate('PSK is most efficient:\nbest BER at same SNR',
                xy=(10, ber_psk_th[int(10 / snr_db_range[-1] * len(snr_db_range))]),
                xytext=(11, 1e-4),
                color='#ce93d8', fontsize=9,
                arrowprops=dict(arrowstyle='->', color='#ce93d8'))

    plt.tight_layout()
    plt.savefig('ber_vs_snr.png', dpi=150, bbox_inches='tight', facecolor='#0e0e12')
    print("✅  BER plot saved → ber_vs_snr.png")
    plt.show()


def main():
    print("\n📈  BER vs SNR Analysis")
    print("    Theoretical formulas + Monte Carlo simulation")
    print("─" * 45)
    print("  ASK : Pe = 0.5 × erfc( √(SNR/4) )")
    print("  FSK : Pe = 0.5 × erfc( √(SNR/2) )")
    print("  PSK : Pe = 0.5 × erfc( √(SNR)   )  ← best")
    print("─" * 45)
    print("  Running simulation (10,000 bits per SNR point)...")

    snr_db_range = np.linspace(0, 15, 200)
    plot_ber(snr_db_range)


if __name__ == "__main__":
    main()