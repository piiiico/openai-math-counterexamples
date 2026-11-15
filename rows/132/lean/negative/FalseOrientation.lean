import Controls
-- Dropping tournament completeness cannot be smuggled into the hypothesis.
example : Family132.TournamentOn {0, 1, 2, 3} (fun _ _ => False) := by
  unfold Family132.TournamentOn
  decide
