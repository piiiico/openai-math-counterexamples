"""Exact budget, malformed-input and boundary controls for the recursive packet."""
from pathlib import Path
import subprocess
import sys
import unittest
import json
import tempfile

if __package__:
    from . import checker,finite_controls
else:
    import checker
    import finite_controls

HERE=Path(__file__).resolve().parent


class AmplificationTests(unittest.TestCase):
    def document(self):
        return json.loads((HERE/'certificate.json').read_text())

    def test_default_cli(self):
        p=subprocess.run([sys.executable,str(HERE/'checker.py')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn('RESULT: certified amplification and readout budgets',p.stdout)

    def test_symbolic_counts_and_multiple_targets(self):
        for target in (1,2,37):
            r=checker.verify(self.document(),HERE,target)
            self.assertEqual(r['stage_count'],{'coefficient':4*target*target,'binary_exponent':1442840692})
            self.assertEqual(r['next_sign_count']['coefficient'],16777218)
            self.assertEqual(r['next_degree_bound']['coefficient'],16777217)
            self.assertEqual(r['copy_count']['power_of_current_sign_count'],2)

    def test_all_seven_false_budgets_reject_optimized(self):
        for c in ('few-copies','short-tail','long-tail','strong-gain','strong-mass','few-stages','fourth-moment'):
            with self.subTest(control=c):
                r=subprocess.run([sys.executable,'-O',str(HERE/'checker.py'),'--negative-control',c],capture_output=True,text=True)
                self.assertEqual(r.returncode,1,r.stdout+r.stderr)
                self.assertIn('RESULT: not certified',r.stderr)

    def test_schema_and_budget_errors(self):
        changes=[('schema_version',2),('copy_log2',True),('copy_log2',511),('copy_log2',0),
                 ('tail_log2',-1),('fourth_moment_upper',0),('mass_log2',-1),('gain_denominator',0),('padding_log2',-1)]
        for key,value in changes:
            d=self.document();d[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):checker.verify(d,HERE)
        for doc in ([],None,dict(self.document(),unexpected=1)):
            with self.assertRaises(ValueError):checker.verify(doc,HERE)
        for target in (0,-1,True,'1'):
            with self.assertRaisesRegex(ValueError,'positive integer'):checker.verify(self.document(),HERE,target)

    def test_small_copy_and_tail_domain_errors(self):
        d=self.document();d['copy_log2']=128
        with self.assertRaisesRegex(ValueError,'positive leaf'):checker.verify(d,HERE)
        d=self.document();d['tail_log2']=2
        with self.assertRaisesRegex(ValueError,'selector region'):checker.verify(d,HERE)

    def test_pins_and_manifest_fail_closed(self):
        d=self.document();d['gaussian']['files']['checker.py']='0'*64
        with self.assertRaisesRegex(ValueError,'hash mismatch'):checker.verify(d,HERE)
        for dep in (None,{}, {'directory':1,'files':{}},{'directory':'x','files':[]}):
            d=self.document();d['gaussian']=dep
            with self.assertRaisesRegex(ValueError,'manifest'):checker.verify(d,HERE)

    def test_missing_or_bad_certificate(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.json';bad.write_text('{bad')
            for file in (bad,Path(tmp)/'missing.json'):
                r=subprocess.run([sys.executable,str(HERE/'checker.py'),'--certificate',str(file)],capture_output=True,text=True)
                self.assertEqual(r.returncode,1)

    def test_finite_controls_and_optimized_output(self):
        outputs=[]
        for optimized in (False,True):
            cmd=[sys.executable]+(['-O'] if optimized else [])+[str(HERE/'checker.py'),'--finite-controls']
            p=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr);outputs.append(p.stdout)
        self.assertEqual(outputs[0],outputs[1])
        r=json.loads(outputs[0].split('\nRESULT:')[0])['finite_controls']
        self.assertTrue(r['score_laws']['one_copy_counterexample']['half_bound_fails'])
        self.assertEqual(r['score_laws']['one_copy_counterexample']['variance'],'16/15')

    def test_comparison_and_degree_mutations_detected(self):
        with self.assertRaisesRegex(ValueError,'comparison'):
            finite_controls.comparison_controls(corrupt=True)
        with self.assertRaisesRegex(ValueError,'degree'):
            finite_controls.fourier_controls(corrupt=True)
        with self.assertRaisesRegex(ValueError,'recurrence'):
            finite_controls.recurrence_controls(corrupt=True)

    def test_undefined_normalization_and_zero_variance_rejected(self):
        for b in (0,-1):
            with self.assertRaisesRegex(ValueError,'positive normalization'):
                finite_controls.compare_normalized(1,b,1)
        constant=finite_controls.observation(2,lambda x:0)
        with self.assertRaisesRegex(ValueError,'variance at least one'):
            finite_controls.check_score_law(constant)

    def test_readout_degree_is_not_ambient_dimension(self):
        r=finite_controls.fourier_controls()['examples'][0]
        self.assertEqual(r['ambient_signs'],6)
        self.assertEqual(r['degree_upper'],2)
        self.assertEqual(r['actual_degree'],2)


if __name__=='__main__':
    unittest.main()
