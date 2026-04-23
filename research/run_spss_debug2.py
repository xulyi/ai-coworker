import spss

spss.StartSPSS()

# Test alternative GET DATA syntax
cmds = [
    "CD '/Users/leyixu/Ai cowork/research'.",
    "GET DATA /TYPE=TXT",
    "  /FILE='stroke_baseline.csv'",
    "  /DELCASE=LINE",
    "  /DELIMITERS=\",\"",
    "  /ARRANGEMENT=DELIMITED",
    "  /FIRSTCASE=2",
    "  /VARIABLES=",
    "  分组 A2",
    "  组别说明 A20",
    "  患者ID A10",
    "  卒中亚型 A4",
    "  时间点 A2",
    "  FMA_LE F3.0",
    "  ADL F3.0",
    "  BBS F3.0",
    "  TUGT A5",
    "  MAS A2",
    "  CSS F3.0.",
]

for i, cmd in enumerate(cmds):
    try:
        spss.Submit(cmd)
        print(f"OK [{i}]: {cmd[:60]}")
    except Exception as e:
        print(f"FAIL [{i}]: {cmd[:60]}")
        print(f"   Error: {e}")
        break

spss.StopSPSS()
