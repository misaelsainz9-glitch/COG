import builtins
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import lanzamiento


class LauncherTests(unittest.TestCase):
    def test_packaged_import_failure_is_reported_without_a_dialog(self):
        original_import = builtins.__import__
        def failing_import(name, *args, **kwargs):
            if name == 'comprobacion_instalacion':
                raise ImportError('missing packaged component')
            return original_import(name, *args, **kwargs)
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / 'report.json'
            with patch.object(sys, 'argv', ['SASISOPA.exe', '--smoke-test', str(report)]), patch('builtins.__import__', side_effect=failing_import):
                self.assertEqual(lanzamiento.run(), 1)
            self.assertIn('missing packaged component', report.read_text(encoding='utf-8'))
