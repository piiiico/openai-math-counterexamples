import WindowPeriodicity
open Family088
-- Consumers proves recurrence and all earlier window equations for this function.
private def badWindow (n : ℕ) : ℚ := if n = 105 ∨ n = 118 then 1 else 0
example : badWindow 131 = 1 * badWindow 118 := by
  decide +kernel
