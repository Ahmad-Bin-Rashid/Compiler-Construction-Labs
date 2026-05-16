program test;
var
  x, y : integer;
  z : real;

{ This is a comment }
begin
  x := 10;
  y := 20;
  z := x + y;

  if x < y then
    z := z + 1
  else
    z := z - 1;

  while x < y do
    x := x + 1;
end.
