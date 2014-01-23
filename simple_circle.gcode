%
( File created using Intuwiz Software Service )
( http://www.intuwiz.com )
( More information: http://www.intuwiz.com/circle.html )
( File created:  2014-01-21  14:49:41  )
( start of program
G00 Z0.5 F70
G00 X-10 Y0 F70
G01 Z-1 F50
( full circle
G02 I10
G00 Z0.5 F70
( first ccw 2nd quadrant
G00 X0 Y0
G03 I10 X10 Y10
( second ccw 4th quadrant
G00 X0 Y20
G03 I-10 X10 Y-10
( third cw 1st quadrant
G00 X00 Y40
G02 I-10 X10 Y10
( last cw 3rd quadrant
G00 X0 Y60
G02 I10 X10 Y-10
(home
G00 X0 Y0 Z0
M30
%
