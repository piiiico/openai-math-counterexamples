import CappedValue
open Family088
-- Replacing c13 by c12 must fail even at the first valid window index.
example : tableValue 113 = simplexWeight 12 * tableValue 100 := by
  decide +kernel
