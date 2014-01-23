(Sample Program G02EX3:)
(Workpiece Size: X4, Y3, Z1)
(Tool: Tool #2, 1/4" Slot Drill)
(Tool Start Position: X0, Y0, Z1)

N2 G90 G80 G40 G54 G20 G17 G50 G94 G64 (safety block)
N5 G90 G20
N10 M06 T2 G43 H2
N15 M03 S1200
N20 G00 X1 Y1
N25 Z0.1
N30 G01 Z-0.1 F5
N35 G02 X2 Y2 I1 J0 F20 (Arc feed CW, radius I1,J0 at 20 ipm)
N40 G01 X3.5
N45 G02 X3 Y0.5 R2 (Arc feed CW, radius 2)
N50 X1 Y1 R2 (Arc feed CW, radius 2)
N55 G00 Z0.1
N60 X2 Y1.5
N65 G01 Z-0.25
N70 G02 X2 Y1.5 I0.25 J-0.25 (Full circle arc feed move CW)
N75 G00 Z1
N80 X0 Y0
N85 M05
N90 M30
