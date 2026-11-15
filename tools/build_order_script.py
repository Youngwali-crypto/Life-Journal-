"""Build the ordering script with the installed game-compatible Python."""
import argparse
import sys
from pathlib import Path
from build_diagnostic import build, SOURCES

ORDER_SOURCES = SOURCES + (
    'life_journal_bootstrap.py', 'life_journal_order_interaction.py',
    'life_journal_order_runtime.py', 'life_journal_saved_store.py',
    'prototypes/game_context.py', 'prototypes/household_payment.py',
    'prototypes/journal_access.py', 'prototypes/journal_access_dialogs.py',
    'prototypes/journal_interface.py', 'prototypes/sims4_journal_dialogs.py',
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True)
    parser.add_argument('--output', type=Path, default=Path('dist/LifeJournalOrders.ts4script'))
    args = parser.parse_args()
    actual = '{}.{}'.format(*sys.version_info[:2])
    if args.python != actual or actual != '3.7':
        parser.error('Use Python 3.7 for the verified game runtime')
    if args.output.suffix != '.ts4script':
        parser.error('Output must end with .ts4script')
    build(Path(__file__).resolve().parents[1], args.output, ORDER_SOURCES)
    print('Built {}'.format(args.output))
