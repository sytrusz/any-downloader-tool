import asyncio
import sys

# Python 3.14+ deprecated and modified asyncio.get_event_loop() to throw a RuntimeError 
# if no loop is running in the current thread. SpotDL spawns threads that use this, 
# which causes a fatal crash. We monkey-patch it here to auto-create a loop if missing.
_old_get_event_loop = getattr(asyncio, "get_event_loop", None)

def _get_event_loop_patch():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

asyncio.get_event_loop = _get_event_loop_patch

from spotdl.console import console_entry_point

if __name__ == "__main__":
    sys.argv = sys.argv[1:] # Remove the wrapper script from args so spotdl parses correctly
    console_entry_point()
