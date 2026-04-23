import spss
import sys

spss.StartSPSS()
print("SPSS version info:")
try:
    spss.Submit("SHOW VERSION.")
    print("SHOW VERSION succeeded")
except Exception as e:
    print(f"Error: {e}")
    spss.Submit("DISPLAY VARS.")
spss.StopSPSS()
