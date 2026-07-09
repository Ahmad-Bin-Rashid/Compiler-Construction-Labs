{ Test 4 — Undeclared identifier error }
{ Expected: ERROR for 'undeclared_var' used on rhs }
program undecl_id ;
var
    x : integer ;
    y : real
begin
    x := 42 ;
    y := undeclared_var + x
end .
