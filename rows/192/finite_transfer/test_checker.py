"""Acceptance, malformed-input and deliberately false-budget controls."""
from pathlib import Path
import subprocess
import sys
import unittest
import json
import tempfile

if __package__:
    from . import checker, finite_controls
else:
    import checker
    import finite_controls

HERE = Path(__file__).resolve().parent


class FiniteTransferTests(unittest.TestCase):
    def document(self):
        return json.loads((HERE/'certificate.json').read_text())

    def test_default_certificate_cli(self):
        result = subprocess.run([sys.executable, str(HERE/'checker.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('RESULT: certified finite-sign predictor gain > Q_N/50', result.stdout)

    def test_exact_cost_and_mass_accounting(self):
        result = checker.verify(self.document(), HERE)
        N, m = 2**512, 2**24+1
        self.assertEqual(result['block_sign_count'], N)
        self.assertEqual(result['total_sign_count'], (m+1)*N)
        self.assertEqual(result['cell_degree_upper_bound'], m*N)
        self.assertEqual(result['product_mass_binary_exponent'], 86*m)
        self.assertEqual(result['certified_gain_ratio_lower'], '1/50')

    def test_all_four_false_budgets_fail_under_optimized_python(self):
        for control in ('small-block','short-tail','strong-margin','strong-mass'):
            with self.subTest(control=control):
                p = subprocess.run([sys.executable,'-O',str(HERE/'checker.py'),
                                    '--negative-control',control], capture_output=True,text=True)
                self.assertEqual(p.returncode,1,p.stdout+p.stderr)
                self.assertIn('RESULT: not certified',p.stderr)

    def test_no_positive_leaf_mass_from_small_block(self):
        d=self.document();d['block_log2']=128
        with self.assertRaisesRegex(ValueError,'positive interval'):
            checker.verify(d,HERE)

    def test_tail_cutoff_cannot_omit_selector_region(self):
        d=self.document();d['tail_cutoff']=7
        with self.assertRaisesRegex(ValueError,'selector cutoff'):
            checker.verify(d,HERE)

    def test_invalid_schemas_and_parameters_are_rejected(self):
        changes=[('schema_version',2),('block_log2',True),('block_log2',511),
                 ('block_log2',0),('tail_cutoff',0),('finite_mass_binary_exponent',-1),
                 ('gain_ratio_lower',{'numerator':1,'denominator':0}),
                 ('gain_ratio_lower',{'numerator':True,'denominator':50}),
                 ('gain_ratio_lower',{'numerator':-1,'denominator':50})]
        for k,v in changes:
            with self.subTest(key=k,value=v):
                d=self.document();d[k]=v
                with self.assertRaises(ValueError): checker.verify(d,HERE)
        d=self.document();d['unrecognized']=1
        with self.assertRaises(ValueError): checker.verify(d,HERE)
        with self.assertRaises(ValueError): checker.verify([],HERE)

    def test_pinned_dependency_rejects_changed_hash(self):
        d=self.document();d['predecessor']['files']['checker.py']='0'*64
        with self.assertRaisesRegex(ValueError,'hash mismatch'): checker.verify(d,HERE)

    def test_invalid_dependency_manifest_rejected(self):
        for dependency in [None,{}, {'directory':1,'files':{}},
                           {'directory':'x','files':[]}]:
            d=self.document();d['predecessor']=dependency
            with self.assertRaises(ValueError): checker.verify(d,HERE)

    def test_missing_and_malformed_certificate_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/'bad.json';bad.write_text('{bad')
            for p in (bad,Path(d)/'missing.json'):
                r=subprocess.run([sys.executable,str(HERE/'checker.py'),'--certificate',str(p)],
                                 capture_output=True,text=True)
                self.assertEqual(r.returncode,1)
                self.assertIn('RESULT: not certified',r.stderr)

    def test_finite_controls_and_optimized_output(self):
        outputs=[]
        for optimized in (False,True):
            cmd=[sys.executable]+(['-O'] if optimized else [])+[str(HERE/'checker.py'),'--finite-controls']
            p=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr);outputs.append(p.stdout)
        self.assertEqual(outputs[0],outputs[1])
        self.assertIn('2125',outputs[0])

    def test_corrupted_deficit_identity_is_detected(self):
        with self.assertRaisesRegex(ValueError,'deficit identity failed'):
            finite_controls.run_controls(corrupt=True)

    def test_discrete_control_domain_and_nonpositive_example(self):
        for invalid in (0,2,5):
            with self.assertRaisesRegex(ValueError,'positive square'):
                finite_controls.binomial_law(invalid)
        with self.assertRaisesRegex(ValueError,'positive mass'):
            finite_controls.interval_moments(finite_controls.binomial_law(4),3,4)
        reports=finite_controls.run_controls()
        self.assertEqual([r['weighted_input_tuples'] for r in reports['reports']],[625,2125])
        self.assertEqual(reports['restricted_moments']['interval_endpoint_cases'],612)
        # A true algebraic identity must also hold for parameters that do not yield a violation.
        self.assertLess(checker.Fraction(reports['reports'][0]['deficit']),0)


if __name__ == '__main__':
    unittest.main()
