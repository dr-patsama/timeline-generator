#!/bin/bash
# Timeline Generator - Setup Script
# Run: open Terminal, then:
#   cd ~/Documents/Timeline\ Generator && chmod +x setup-app.sh && ./setup-app.sh

APP_DIR="$HOME/Documents/Timeline Generator/Timeline Generator.app"
ICONSET="$APP_DIR/Contents/Resources/AppIcon.iconset"
ICNS="$APP_DIR/Contents/Resources/AppIcon.icns"

echo "🔧 Setting up Timeline Generator app..."

# 1. Convert iconset to icns if needed
if [ -d "$ICONSET" ]; then
    iconutil -c icns "$ICONSET" -o "$ICNS" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ App icon created"
        rm -rf "$ICONSET"
    else
        echo "⚠️  Could not create .icns icon (cosmetic only, app still works)"
    fi
fi

# 2. Compile AppleScript that calls our launch script
echo 'do shell script "bash \"$HOME/Documents/Timeline Generator/Timeline Generator.app/Contents/MacOS/launch\" &> /tmp/timeline-launch.log &"' > /tmp/timeline_main.applescript
osacompile -o "$APP_DIR/Contents/Resources/Scripts/main.scpt" /tmp/timeline_main.applescript
echo "✅ AppleScript compiled"

# 3. Make launch script executable
chmod +x "$APP_DIR/Contents/MacOS/launch"
echo "✅ Launch script ready"

# 4. Remove quarantine
xattr -dr com.apple.quarantine "$APP_DIR" 2>/dev/null
echo "✅ Quarantine removed"

# 5. Copy to /Applications
cp -R "$APP_DIR" /Applications/
xattr -dr com.apple.quarantine /Applications/Timeline\ Generator.app 2>/dev/null
echo "✅ Copied to /Applications"

# 6. Register with Launch Services
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/Timeline\ Generator.app 2>/dev/null

rm -f /tmp/timeline_main.applescript

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To use:"
echo "  • Open 'Timeline Generator' from Launchpad or /Applications"
echo "  • Or drag it to your Dock for quick access"
echo "  • It starts the server and opens in your browser automatically"
echo ""
