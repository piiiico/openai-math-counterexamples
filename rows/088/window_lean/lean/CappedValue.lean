import ConcreteCertificate

namespace Family088

/-- A concrete total sequence computing the cap19 maximum recurrence.
The value at1 is the zero sentinel for an unreachable partition size. -/
def cappedValue (n : ℕ) : ℚ :=
  if _hn0 : n = 0 then 1 else
  if _hn1 : n = 1 then 0 else
  ((List.range 19).map fun j =>
    if _hj : j + 1 ≤ n then
      simplexWeight (j + 1) * cappedValue (n - (j + 1)) else 0).foldr max 0
termination_by n
decreasing_by omega

theorem cappedValue_zero : cappedValue 0 = 1 := by rw [cappedValue]; rfl

theorem cappedValue_one : cappedValue 1 = 0 := by rw [cappedValue]; rfl

theorem cappedValue_recurrence (n : ℕ) (hn : 2 ≤ n) :
    cappedValue n = boundedStep simplexWeight cappedValue 19 n := by
  rw [cappedValue]
  simp only [dif_neg (show n ≠ 0 by omega), dif_neg (show n ≠ 1 by omega)]
  rfl

theorem cappedValue_agrees (n : ℕ) (hn : n ≤ 131) :
    cappedValue n = tableValue n :=
  prefix_agreement simplexWeight cappedValue tableValue 19 131
    (by simpa [tableValue, values] using cappedValue_zero)
    (by simpa [tableValue, values] using cappedValue_one)
    cappedValue_recurrence table_recurrence n hn

/-- Unconditional period theorem for the defined cap19 recurrence sequence. -/
theorem cappedValue_periodicity (n : ℕ) (hn : 100 ≤ n) :
    cappedValue (n + 13) = simplexWeight 13 * cappedValue n :=
  capped_recurrence_periodicity cappedValue cappedValue_zero cappedValue_one
    cappedValue_recurrence n hn

theorem cappedValue_boundary : cappedValue 112 > simplexWeight 13 * cappedValue 99 := by
  rw [cappedValue_agrees 112 (by omega), cappedValue_agrees 99 (by omega)]
  exact table_boundary

/-- The starting point100 is minimal for a period identity valid at every later index. -/
theorem no_earlier_uniform_cutoff (B : ℕ) (hB : B < 100) :
    ¬ (∀ n, B ≤ n → cappedValue (n + 13) = simplexWeight 13 * cappedValue n) := by
  intro h
  have h99 := h 99 (by omega)
  have hstrict := cappedValue_boundary
  change cappedValue 112 = simplexWeight 13 * cappedValue 99 at h99
  linarith

#print axioms cappedValue_periodicity
#print axioms cappedValue_boundary
#print axioms no_earlier_uniform_cutoff
end Family088
