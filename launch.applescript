-- Timeline Generator Launcher
-- Starts local servers and opens the app in Safari

-- Check if save server (port 8012) is already running, start if not
try
	do shell script "lsof -i:8012 | grep LISTEN"
on error
	do shell script "/opt/homebrew/bin/python3.11 '/Users/drpat/Documents/Timeline Generator/server.py' > /dev/null 2>&1 &"
end try

-- Check if web server (port 8080) is already running, start if not
try
	do shell script "lsof -i:8080 | grep LISTEN"
on error
	do shell script "/opt/homebrew/bin/python3.11 -m http.server 8080 --directory '/Users/drpat/Documents/Timeline Generator' --bind 127.0.0.1 > /dev/null 2>&1 &"
end try

delay 1
open location "http://localhost:8080"
