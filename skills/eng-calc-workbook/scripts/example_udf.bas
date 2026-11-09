Attribute VB_Name = "modCalc_bearing"
Option Explicit

' Basic rating life of a rolling bearing, ISO 281.
'   C [kN] dynamic load rating, P [kN] equivalent load, p [-] 3 ball / 10/3 roller, n [1/min] speed
'   returns L10h [h]
Public Function L10h(ByVal C As Double, ByVal P As Double, ByVal pExp As Double, ByVal n As Double) As Double
    If P <= 0 Or n <= 0 Then Err.Raise vbObjectError + 1, "L10h", "P and n must be > 0"
    L10h = 10 ^ 6 * (C / P) ^ pExp / (60 * n)
End Function

' Run by vba_run.ps1 -Run Test_L10h; raises on a mismatch.
Public Sub Test_L10h()
    ' 6205: C = 14.8 kN, P = 2 kN, ball, 1500 1/min -> (7.4)^3 * 1e6 / 90000 = 4502.5 h
    Dim x As Double
    x = L10h(14.8, 2, 3, 1500)
    If Abs(x - 4502.49) > 0.01 Then Err.Raise vbObjectError + 100, "Test_L10h", "L10h = " & x & ", expected 4502.49"
End Sub
