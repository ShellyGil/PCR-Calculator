#!/usr/bin/env python3
import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- Configuration Constants ---
PER_SAMPLE_TOTAL = 11.0  # Total reaction volume per sample (µL)
PRIMER_PER = 0.5         # Volume of each primer per sample (µL)
DEFAULT_EXCESS = 10.0    # Default excess percentage
DEFAULT_SAMPLES = 8

class PCRLogic:
    """Handles the core math for the PCR calculations."""
    
    @staticmethod
    def round_to_half(x: float) -> float:
        """Rounds a float to the nearest 0.5."""
        return round(x * 2) / 2.0

    @staticmethod
    def calculate(n_samples: int, excess_percent: float, mix_x: int):
        """
        Returns a tuple: (per_sample_dict, total_mix_dict, grand_total_vol)
        """
        if mix_x not in (2, 5):
            raise ValueError("Mix concentration must be 2 or 5.")
        
        # 1. Calculate Per Sample (Fixed logic based on 11uL total)
        # Target: Equivalent of 6uL of 2X mix in an 11uL reaction
        mix_vol = 6.0 * (2.0 / mix_x)
        primers_total = 2 * PRIMER_PER
        ddw_vol = PER_SAMPLE_TOTAL - (mix_vol + primers_total)
        
        if ddw_vol < 0:
            raise ValueError("Computed DDW volume is negative.")

        per_sample = {
            "DDW": ddw_vol,
            f"Mix ({mix_x}X)": mix_vol,
            "Primer Fwd": PRIMER_PER,
            "Primer Rev": PRIMER_PER,
        }

        # 2. Calculate Totals (Master Mix)
        factor = 1.0 + (excess_percent / 100.0)
        # We calculate the exact required, then round the final ingredient amount
        totals = {k: PCRLogic.round_to_half(v * n_samples * factor) for k, v in per_sample.items()}
        
        grand_total = sum(totals.values())
        
        return per_sample, totals, grand_total

    @staticmethod
    def format_text_report(n, exc, mx, per, tot, grand):
        lines = [
            f"PCR Report | Samples: {n} | Excess: {exc}% | Mix: {mx}X",
            "=" * 50,
            f"{'INGREDIENT':<20} | {'PER SAMPLE':>10} | {'MASTER MIX':>12}",
            "-" * 50
        ]
        for k, v in per.items():
            lines.append(f"{k:<20} | {v:>7.1f} µL | {tot[k]:>9.1f} µL")
        lines.append("-" * 50)
        lines.append(f"{'TOTAL VOLUME':<20} | {PER_SAMPLE_TOTAL:>7.1f} µL | {grand:>9.1f} µL")
        return "\n".join(lines)


class PCRGui:
    """Modern Tkinter GUI for the calculator."""
    
    def __init__(self, root, default_samples, default_excess, default_mix, save_path=None):
        self.root = root
        self.root.title("PCR Master Mix Calculator")
        self.root.geometry("600x550")
        self.root.minsize(500, 500)
        
        # State Variables
        self.var_samples = tk.IntVar(value=default_samples)
        self.var_excess = tk.DoubleVar(value=default_excess)
        self.var_mix = tk.StringVar(value=f"{default_mix}X")
        self.save_path = save_path

        # Triggers for real-time updates
        self.var_samples.trace_add("write", self.update_calc)
        self.var_excess.trace_add("write", self.update_calc)
        self.var_mix.trace_add("write", self.update_calc)

        self._setup_styles()
        self._build_layout()
        self.update_calc() # Initial run

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # Usually cleaner than default
        
        # Customizing fonts and colors
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground="#333")
        style.configure("BigResult.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0055aa")
        style.configure("Error.TLabel", foreground="red")
        style.configure("Card.TFrame", background="#f0f0f0", relief="groove")

    def _build_layout(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # --- Section 1: Inputs ---
        input_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=15)
        input_frame.pack(fill="x", pady=(0, 20))

        # Samples Row
        ttk.Label(input_frame, text="Samples:").grid(row=0, column=0, sticky="w")
        self.spin_samples = ttk.Spinbox(input_frame, from_=1, to=999, textvariable=self.var_samples, width=6)
        self.spin_samples.grid(row=0, column=1, padx=10, sticky="w")
        
        # Slider for samples (Quick adjust)
        self.scale_samples = ttk.Scale(input_frame, from_=1, to=96, variable=self.var_samples, orient="horizontal")
        self.scale_samples.grid(row=0, column=2, sticky="ew", padx=10)
        input_frame.columnconfigure(2, weight=1)

        # Excess Row
        ttk.Label(input_frame, text="Excess (%):").grid(row=1, column=0, sticky="w", pady=10)
        ttk.Spinbox(input_frame, from_=0, to=50, increment=0.5, textvariable=self.var_excess, width=6).grid(row=1, column=1, padx=10, sticky="w", pady=10)

        # Mix Row
        ttk.Label(input_frame, text="Mix Type:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(input_frame, values=["2X", "5X"], textvariable=self.var_mix, state="readonly", width=5).grid(row=2, column=1, padx=10, sticky="w")

        # --- Section 2: Results Display ---
        # We use a Treeview for a clean table look instead of raw text
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        cols = ("Ingredient", "Per Sample (µL)", "Master Mix (µL)")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=6)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        
        self.tree.pack(fill="both", expand=True)

        # --- Section 3: Grand Total Highlight ---
        total_frame = ttk.Frame(main_frame, padding=(0, 20, 0, 10))
        total_frame.pack(fill="x")
        
        ttk.Label(total_frame, text="Total Master Mix Volume:", style="Header.TLabel").pack(anchor="center")
        self.lbl_grand_total = ttk.Label(total_frame, text="---", style="BigResult.TLabel")
        self.lbl_grand_total.pack(anchor="center")
        
        self.lbl_status = ttk.Label(main_frame, text="", style="Error.TLabel")
        self.lbl_status.pack(anchor="w")

        # --- Section 4: Action Buttons ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_frame, text="Save Report", command=self.save_report).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def get_inputs(self):
        try:
            n = self.var_samples.get()
            e = self.var_excess.get()
            m_str = self.var_mix.get().replace("X", "")
            m = int(m_str)
            if n < 1: raise ValueError("Samples < 1")
            if e < 0: raise ValueError("Excess < 0")
            return n, e, m
        except Exception:
            return None

    def update_calc(self, *args):
        inputs = self.get_inputs()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not inputs:
            self.lbl_grand_total.config(text="Invalid Input", foreground="red")
            self.lbl_status.config(text="Please check your input values.")
            return

        n, exc, mx = inputs
        try:
            per, tot, grand = PCRLogic.calculate(n, exc, mx)
            
            # Populate Table
            for k in per.keys():
                # Highlight rows differently if needed, or just insert
                self.tree.insert("", "end", values=(k, f"{per[k]:.1f}", f"{tot[k]:.1f}"))
            
            # Update Grand Total
            self.lbl_grand_total.config(text=f"{grand:.1f} µL", foreground="#0055aa")
            self.lbl_status.config(text="") # Clear errors
            
            # Store current results for export
            self.current_report = PCRLogic.format_text_report(n, exc, mx, per, tot, grand)
            
        except ValueError as e:
            self.lbl_status.config(text=str(e))

    def copy_to_clipboard(self):
        if hasattr(self, 'current_report'):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_report)
            messagebox.showinfo("Copied", "Report copied to clipboard!")

    def save_report(self):
        if not hasattr(self, 'current_report'): return
        
        path = self.save_path
        if not path:
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Save PCR Report"
            )
        
        if path:
            try:
                with open(path, "w") as f:
                    f.write(self.current_report)
                messagebox.showinfo("Saved", f"Saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

def run_cli_mode(args):
    """Runs the non-GUI version."""
    try:
        if args.samples is None:
            # Simple interactive mode for CLI
            print("--- PCR Calculator (CLI) ---")
            s_in = input("Number of samples: ")
            e_in = input(f"Excess % [{DEFAULT_EXCESS}]: ")
            m_in = input(f"Mix (2 or 5) [2]: ")
            
            n = int(s_in) if s_in else DEFAULT_SAMPLES
            exc = float(e_in) if e_in else DEFAULT_EXCESS
            mx = int(m_in) if m_in else 2
        else:
            n = args.samples
            exc = args.excess
            mx = args.mix
            
        per, tot, grand = PCRLogic.calculate(n, exc, mx)
        report = PCRLogic.format_text_report(n, exc, mx, per, tot, grand)
        print("\n" + report + "\n")
        
        if args.save:
            with open(args.save, 'w') as f:
                f.write(report)
            print(f"[+] Saved to {args.save}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="PCR Genotyping Master Mix Calculator")
    parser.add_argument("-n", "--samples", type=int, help="Number of samples")
    parser.add_argument("-e", "--excess", type=float, default=DEFAULT_EXCESS, help="Excess percentage")
    parser.add_argument("-m", "--mix", type=int, choices=[2, 5], default=2, help="Mix concentration (2X or 5X)")
    parser.add_argument("-s", "--save", type=str, help="Auto-save report to file")
    parser.add_argument("--no-gui", action="store_true", help="Force command line interface")
    
    args = parser.parse_args()

    # Determine mode
    gui_available = True
    try:
        import tkinter
    except ImportError:
        gui_available = False

    if args.no_gui or not gui_available:
        run_cli_mode(args)
    else:
        # Start GUI
        root = tk.Tk()
        # If arguments were passed via CLI, use them as defaults in GUI
        d_n = args.samples if args.samples else DEFAULT_SAMPLES
        d_e = args.excess
        d_m = args.mix
        
        app = PCRGui(root, d_n, d_e, d_m, save_path=args.save)
        root.mainloop()

if __name__ == "__main__":
    main()