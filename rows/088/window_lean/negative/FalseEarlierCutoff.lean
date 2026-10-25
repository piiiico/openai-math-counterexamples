import CappedValue
open Family088
-- False exact window identity at99; the kernel must reject it.
example : tableValue 112 = simplexWeight 13 * tableValue 99 := by
  decide +kernel
