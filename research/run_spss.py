import spss
import spssaux
import sys

syntax_file = "/Users/leyixu/Ai cowork/research/baseline_analysis.sps"
output_file = "/Users/leyixu/Ai cowork/research/baseline_results.spv"

print("Starting SPSS backend...")
spss.StartSPSS()
print("SPSS started.")

print(f"Submitting syntax file: {syntax_file}")
with open(syntax_file, 'r', encoding='utf-8') as f:
    syntax = f.read()

try:
    spss.Submit(syntax)
    print("Syntax executed successfully.")
    
    # Save output document
    spss.Submit(f"OUTPUT SAVE OUTFILE='{output_file}'.")
    print(f"Output saved to: {output_file}")
except Exception as e:
    print(f"Error during execution: {e}")
    sys.exit(1)
finally:
    spss.StopSPSS()
    print("SPSS stopped.")
