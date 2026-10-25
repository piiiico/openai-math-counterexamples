import CappedValue

namespace Family088.Controls

example (weight M : ℕ → ℚ) (B P : ℕ)
    (hrec : ∀ n, B ≤ n → M n = 0) :
    ∀ n, B ≤ n → M (n + P) = (0 : ℚ) * M n := by
  apply window_periodicity weight M B 0 P 0 (by norm_num)
  · intro n hn
    simpa [step] using hrec n hn
  · intro n hn hlt
    omega

example (xs : List ℚ) :
    (xs.map ((0 : ℚ) * ·)).foldr max 0 = 0 := by
  simpa using fold_max_scale xs 0 (le_refl 0)

example :
    ((([-1] : List ℚ).map ((-1 : ℚ) * ·)).foldr max 0) ≠
    (-1 : ℚ) * (([-1] : List ℚ).foldr max 0) := by norm_num

example : (119 + 13 - 19 : ℕ) = (119 - 19) + 13 := by decide
example : (5 + 13 - 19 : ℕ) ≠ (5 - 19) + 13 := by decide

example : boundedStep (fun _ => (1 : ℚ)) (fun _ => 1) 19 0 = 0 := by
  norm_num [boundedStep, List.range_succ]
example : step (fun _ => (1 : ℚ)) (fun _ => 1) 19 0 = 1 := by
  norm_num [step, List.range_succ]

private def badWindow (n : ℕ) : ℚ := if n = 105 ∨ n = 118 then 1 else 0

example : ∀ n, 119 ≤ n → badWindow n = step (fun _ => 0) badWindow 19 n := by
  intro n hn
  have h105 : n ≠ 105 := by omega
  have h118 : n ≠ 118 := by omega
  norm_num [badWindow, h105, h118, step, List.range_succ]

example : ∀ n, 100 ≤ n → n < 118 → badWindow (n + 13) = 1 * badWindow n := by
  intro n hn hlt
  have hh : (n + 13 = 105 ∨ n + 13 = 118) ↔ (n = 105 ∨ n = 118) := by omega
  simp only [badWindow, hh, one_mul]

example : badWindow (118 + 13) ≠ 1 * badWindow 118 := by
  norm_num [badWindow]

example : cappedValue 113 = simplexWeight 13 * cappedValue 100 :=
  cappedValue_periodicity 100 (by omega)
example : cappedValue 131 = simplexWeight 13 * cappedValue 118 :=
  cappedValue_periodicity 118 (by omega)
example : cappedValue 132 = simplexWeight 13 * cappedValue 119 :=
  cappedValue_periodicity 119 (by omega)
example : cappedValue 112 ≠ simplexWeight 13 * cappedValue 99 :=
  ne_of_gt cappedValue_boundary

end Family088.Controls

namespace Family088.Controls
example : Family088.values.size = 132 := by decide +kernel
example : tableValue 132 = 0 := by decide +kernel
example : tableValue 113 ≠ simplexWeight 12 * tableValue 100 := by decide +kernel
end Family088.Controls
