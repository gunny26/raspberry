%
( File created using Intuwiz Software Service )
( http://www.intuwiz.com )
( More information: http://www.intuwiz.com/circle.html )
( File created:  2014-01-21  14:49:41  )

G00 Z0.5 F70
G00 X-10 Y0 F70
G01 Z-1 F50
G02 I10
G00 Z0.5 F70
( first
G00 X0 Y0 F70
G00 X10
G02 I10 X20 Y10
( second
G00 X0 Y0 Z0
G00 X10
G03 I10 X20 Y-10
( third
G00 X0 Y0 Z0
G00 X30 Y0
G02 I-10 X20 Y10
( last
G00 X0 Y0 Z0
G00 X30 Y0
G02 I-10 X20 Y-10
G00 X0 Y0 Z0
M30
%
