{ Test 2 — Valid if-else and while loop }
program valid_control ;
var
    a : integer ;
    b : integer ;
    i : integer
begin
    a := 10 ;
    b := 0 ;
    i := 0 ;
    if a then
        b := a * 2
    else
        b := a - 1 ;
    while i do
        i := i + 1
end .
