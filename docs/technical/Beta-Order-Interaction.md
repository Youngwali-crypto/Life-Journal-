# Phone and computer order interaction

Both tuning resources should point to `OrderLifeJournalInteraction` in
`life_journal_order_interaction`. The class uses the acting Sim for both
surfaces. It calls the shared order dialog and rejects calls before bootstrap
or after the bound lot has ended. The runtime must call `bind_order_dialogs`
with a resolver after zone startup. The resolver must verify the loaded save,
Sim and household and construct `JournalAccessDialogs` with a current-session
guard and a paid wallet adapter.

Build and validate separate phone and computer tuning against the installed game.
Keep both actions player-directed. Provide the localized display name
**Order Life Journal**. Package the tuning resources alongside the script.
The XML Injector supports adding interactions, but the project has not selected
an injection dependency for this beta.

The household funds adapter must recognize an already-applied debit using the
same order ID after an interrupted purchase. A balance check or memory-only
deduplication is insufficient across reload. Establish a verified save-backed
payment strategy before binding the action. No game funds are touched by this
script without a configured wallet adapter.

In a disposable save, order on the phone, then select the same action on a
computer. Verify one §200 charge, one order and the same next-day 9 AM due time.
Also test insufficient funds, travel and save reload.

- [S4CL interaction source](https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/classes/interactions/common_super_interaction.py)
- [XML Injector](https://scumbumbomods.com/xml-injector)
