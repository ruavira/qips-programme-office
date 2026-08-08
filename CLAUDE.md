# Claude working instructions

Follow `AGENTS.md` in full. The repository, not the chat history, is the project memory.

**Start with `HANDOFF.md`.** It is the current baton and it is maintained in both directions —
prepend to its STATE log when you hand back, never edit an older block.

**If you are a Cowork session with a device bridge, inventory your channels BEFORE building
anything.** Call `get_device_info` first. The owner's repository and built site are not connected
by default; request `~/qips-programme-office` and `~/qips-site` together in one dialog. A previous
session spent a working day asking the owner to run `find`, `git log` and `head` and paste the
output back, because it never checked whether it could read his disk itself. Read his files. Do not
use him as a terminal. Git writes still belong in his own shell — the bridge cannot remove an
index lock.

On every new session, read the current canon, open questions and target workstream state before continuing. Work on a branch, keep draft work inside the owning workstream, and return a pull request or a clearly identified patch. Never modify canon without a recorded CCC verdict.
