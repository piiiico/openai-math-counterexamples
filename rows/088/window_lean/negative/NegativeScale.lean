import WindowPeriodicity
open Family088
-- A negative scale does not distribute through maximum with zero padding.
example :
    ((([-1] : List ℚ).map ((-1 : ℚ) * ·)).foldr max 0) =
    (-1 : ℚ) * (([-1] : List ℚ).foldr max 0) := by
  decide +kernel
