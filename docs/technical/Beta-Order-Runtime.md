# Ordering runtime

The order interaction now binds the confirmation dialog on a loaded home lot and charges the acting Sim's household §200 through S4CL. Orders retain the next-day 9 AM due time.

The new SavedJournalStore uses S4CL hidden-household persistence. Orders and receipts are part of the running game and persist when the player saves. Save/reload, Save As, travel and exiting without saving require in-game verification. This starts a new game-save-backed store without importing older prototype JSON files.

Separate payment receipts allow retry after an order-record failure. An uncertain payment blocks further charges and displays an error. Balance differences confirm the charge synchronously. The game must not yield during payment.

Build with `py -3.7 tools/build_order_script.py --python 3.7`. Output is `dist/LifeJournalOrders.ts4script`. It includes the diagnostic module, so remove the diagnostic script when testing this build to avoid duplicate modules. S4CL, XML Injector and an accompanying tuning package are required. The script alone does not add the menu.

The binding handles initial orders. Front-door delivery, planner transfer and missing-planner detection for replacements remain integration work. The confirmation shows the planned delivery time. This is not a complete delivery beta.

Local tests cover insufficient funds, stale identity, receipt reuse, interrupted payments and retry after journal write failure. They do not verify the game runtime.
