"""Unit and integration tests for check.py (standard library only)."""

import contextlib
import io
import itertools
import unittest

import check


def random_label(seed):
    """A deterministic non-symmetric labelling with values in [3], for testing the search."""
    def label(i, j):
        return 1 + (i * 7919 + j * 104729 + seed * 31) % 3
    return label


class TestLabel(unittest.TestCase):
    def test_values_and_symmetry(self):
        self.assertEqual(check.msb_label(1, 2), 1)   # 0 vs 1
        self.assertEqual(check.msb_label(1, 3), 2)   # 0 vs 2
        self.assertEqual(check.msb_label(4, 5), 3)   # 3 vs 4
        self.assertEqual(check.msb_label(5, 4), 3)

    def test_diagonal_rejected(self):
        with self.assertRaises(ValueError):
            check.msb_label(3, 3)

    def test_height(self):
        self.assertEqual([check.height(k) for k in (2, 3, 4, 5, 8, 9)], [1, 2, 2, 3, 3, 4])
        self.assertEqual(check.height(2 * 81 * 81 + 1), 14)
        with self.assertRaises(ValueError):
            check.height(1)

    def test_isqrt_ceil(self):
        self.assertEqual([check.isqrt_ceil(n) for n in (1, 2, 4, 5, 81, 82)], [1, 2, 2, 3, 9, 10])


class TestTournaments(unittest.TestCase):
    def test_cyclic_regular(self):
        for M in (1, 2, 3):
            adj = check.cyclic_tournament(M)
            self.assertTrue(check.is_tournament(adj))
            self.assertEqual(set(check.outdegrees(adj)), {M * M})

    def test_transitive_and_random_are_tournaments(self):
        self.assertTrue(check.is_tournament(check.transitive_tournament(6)))
        self.assertTrue(check.is_tournament(check.transitive_tournament(6, reverse=True)))
        self.assertTrue(check.is_tournament(check.pseudorandom_tournament(9, 3)))

    def test_is_tournament_rejects(self):
        adj = check.transitive_tournament(4)
        adj[2][3] = adj[3][2] = True
        self.assertFalse(check.is_tournament(adj))
        adj = check.transitive_tournament(4)
        adj[2][2] = True
        self.assertFalse(check.is_tournament(adj))


class TestBadSetSearch(unittest.TestCase):
    """The backtracking search agrees with exhaustive subset enumeration."""

    def test_search_matches_bruteforce(self):
        cases = [check.cyclic_tournament(2), check.transitive_tournament(10),
                 check.pseudorandom_tournament(12, 7), check.pseudorandom_tournament(13, 8)]
        for adj in cases:
            for label in (check.msb_label, random_label(1), random_label(2)):
                found = check.max_bad_set(adj, label)
                self.assertTrue(check.is_bad(adj, label, found))
                self.assertEqual(len(found), check.max_bad_size_bruteforce(adj, label))

    def test_cyclic_m3_bruteforce(self):
        adj = check.cyclic_tournament(3)  # k = 19, all 2^19 subsets
        self.assertEqual(check.max_bad_size_bruteforce(adj, check.msb_label), 5)

    def test_every_tournament_on_at_most_six_vertices(self):
        # Lemma A on all 2^(k choose 2) labelled tournaments for k <= 6.
        for k in range(2, 7):
            pairs = list(itertools.combinations(range(1, k + 1), 2))
            worst = 0
            for mask in range(1 << len(pairs)):
                adj = [[False] * (k + 1) for _ in range(k + 1)]
                for b, (i, j) in enumerate(pairs):
                    if mask >> b & 1:
                        adj[i][j] = True
                    else:
                        adj[j][i] = True
                worst = max(worst, len(check.max_bad_set(adj, check.msb_label)))
            self.assertLessEqual(worst, check.height(k) + 1, k)

    def test_constant_label_everything_bad(self):
        adj = check.pseudorandom_tournament(8, 1)
        self.assertEqual(len(check.max_bad_set(adj, check.const_label)), 8)

    def test_stop_at(self):
        adj = check.transitive_tournament(16)
        self.assertEqual(len(check.max_bad_set(adj, check.const_label, stop_at=3)), 3)

    def test_tight_example(self):
        for k in (2, 5, 8, 9, 100):
            ex = check.tight_example(k)
            self.assertEqual(len(set(ex)), check.height(k) + 1)
            self.assertTrue(check.is_bad(check.transitive_tournament(k), check.msb_label, ex))


class TestParameters(unittest.TestCase):
    def test_manuscript_parameters(self):
        self.assertEqual(check.manuscript_parameters(81)["t"], 16)
        self.assertEqual(check.manuscript_parameters(729)["h"], 21)

    def test_epsilon_condition_threshold(self):
        def holds(M):
            p = check.manuscript_parameters(M)
            return check.epsilon_condition(M, check.isqrt_ceil(M), p["t"])
        self.assertFalse(holds(56))
        self.assertTrue(all(holds(M) for M in range(57, 2000)))

    def test_fit_threshold(self):
        self.assertGreater(check.manuscript_parameters(289)["h"], check.isqrt_ceil(289))
        self.assertLessEqual(check.manuscript_parameters(290)["h"], check.isqrt_ceil(290))


class TestMain(unittest.TestCase):
    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            status = check.main(list(args))
        return status, out.getvalue()

    def test_passes(self):
        status, out = self.run_main()
        self.assertEqual(status, 0)
        self.assertTrue(out.rstrip().endswith("RESULT: passes"))
        self.assertNotIn("[FAIL]", out)

    def test_negative_controls_fail(self):
        for control in check.CONTROLS:
            status, out = self.run_main("--negative-control", control)
            self.assertEqual(status, 1, control)
            self.assertTrue(out.rstrip().endswith("RESULT: fails"), control)


if __name__ == "__main__":
    unittest.main()
