{ Test 5 — Multiple errors: both duplicate and undeclared }
{ Expected: ERROR duplicate 'a', ERROR undeclared 'ghost' }
program multi_errors ;
var
    a : integer ;
    b : real ;
    a : integer
begin
    a := ghost + 1 ;
    b := a * 2
end .
