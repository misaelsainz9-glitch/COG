"""Run public tests and expose diagnostics in GitHub's public annotations."""
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests'))
for test, detail in result.failures + result.errors:
    message = (str(test) + '\n' + detail).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print('::error::' + message, flush=True)
summary = f'{result.testsRun} tests; {len(result.failures)} failures; {len(result.errors)} errors; {len(result.skipped)} skipped.'
print('::notice::' + summary, flush=True)
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
        stream.write(summary + '\n')
sys.exit(0 if result.wasSuccessful() else 1)
