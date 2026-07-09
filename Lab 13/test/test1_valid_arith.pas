{ Test 1 — Valid Pascal program with multiple variables and arithmetic }
program valid_arith ;
var
    x      : integer ;
    y      : integer ;
    result : real
begin
    x      := 10 ;
    y      := 3 ;
    result := ( x + y ) * ( x - y )
end .
