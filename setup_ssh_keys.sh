#!/bin/bash
# Setup SSH keys for ARC Connect passwordless login

echo "=== ARC Connect - SSH Key Setup ==="
echo ""
echo "This will set up passwordless SSH for the terminal"
echo ""

# Check if SSH directory exists
if [ ! -d "$HOME/.ssh" ]; then
    echo "📁 Creating .ssh directory..."
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
fi

# Check if SSH key already exists
if [ -f "$HOME/.ssh/id_rsa" ]; then
    echo "✅ SSH key already exists"
else
    echo "🔑 Generating SSH key..."
    ssh-keygen -t rsa -N "" -f "$HOME/.ssh/id_rsa" -q
    echo "✅ SSH key generated"
fi

# Add key to authorized_keys
if [ -f "$HOME/.ssh/id_rsa.pub" ]; then
    echo "🔐 Adding key to authorized_keys..."
    
    # Create authorized_keys if it doesn't exist
    touch "$HOME/.ssh/authorized_keys"
    chmod 600 "$HOME/.ssh/authorized_keys"
    
    # Check if key is already in authorized_keys
    KEY_CONTENT=$(cat "$HOME/.ssh/id_rsa.pub")
    if grep -Fxq "$KEY_CONTENT" "$HOME/.ssh/authorized_keys" 2>/dev/null; then
        echo "✅ Key already in authorized_keys"
    else
        cat "$HOME/.ssh/id_rsa.pub" >> "$HOME/.ssh/authorized_keys"
        echo "✅ Key added to authorized_keys"
    fi
fi

# Test SSH connection
echo ""
echo "🧪 Testing SSH connection..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 localhost exit 2>/dev/null; then
    echo "✅ SUCCESS! SSH passwordless login works!"
    echo ""
    echo "🎉 You can now use the ARC Connect terminal!"
    echo ""
    echo "Next steps:"
    echo "  1. Restart ARC Connect: ./start_arc_connect.sh"
    echo "  2. Go to: http://$(hostname -I | awk '{print $1}'):5001/"
    echo "  3. Click 'Terminal' tab"
    echo "  4. Start typing commands!"
else
    echo "⚠️  SSH test failed"
    echo ""
    echo "Please try manually:"
    echo "  ssh localhost"
    echo ""
    echo "If it asks for a password, check:"
    echo "  1. SSH is running: sudo systemctl status ssh"
    echo "  2. Permissions are correct: ls -la ~/.ssh"
fi

echo ""
echo "=== Setup Complete ==="

