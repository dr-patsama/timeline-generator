-- Timeline Generator Launcher
-- Starts local server and opens the app in browser

set homeDir to POSIX path of (path to home folder)
set appDir to homeDir & "Documents/Timeline Generator"

-- Check if server (port 8012) is already running, start if not
try
	do shell script "lsof -i:8012 | grep LISTEN"
on error
	do shell script "/usr/bin/python3 '" & appDir & "/server.py' > /dev/null 2>&1 &"
end try

delay 1
open location "http://127.0.0.1:8012"
