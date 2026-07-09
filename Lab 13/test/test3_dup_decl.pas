{ Test 3 — Duplicate declaration error }
{ Expected: ERROR on the second declaration of 'count' }
program dup_decl ;
var
    count : integer ;
    total : real ;
    count : integer
begin
    count := 5 ;
    total := count + 1
end .
