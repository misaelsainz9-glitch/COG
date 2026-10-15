import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import rutas_app


class UserDirectoryTests(unittest.TestCase):
    def test_source_keeps_existing_working_directory(self):
        with patch.object(sys, 'frozen', False, create=True):
            self.assertEqual(rutas_app.user_root(), rutas_app.RESOURCE_ROOT)

    def test_installed_data_is_outside_executable_resources(self):
        with tempfile.TemporaryDirectory(prefix='datos con espacios ') as temporary:
            with patch.dict(os.environ, {'LOCALAPPDATA': temporary}), patch.object(sys, 'frozen', True, create=True):
                directory = rutas_app.user_root()
                self.assertEqual(directory, Path(temporary) / 'SASISOPA' / 'Datos')
                self.assertNotEqual(directory, rutas_app.RESOURCE_ROOT)
