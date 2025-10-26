#!/bin/bash
# Fix SSH for ARC Connect

echo "=== ARC Connect - SSH Setup ==="
echo ""

# Check if SSH is installed
if ! command -v sshd &> /dev/null; then
    echo "❌ SSH server not installed"
    echo "📦 Installing OpenSSH server..."
    sudo apt-get update
    sudo apt-get install -y openssh-server
else
    echo "✅ SSH server is installed"
fi

# Check if SSH is running
if ! sudo systemctl is-active --quiet ssh; then
    echo "❌ SSH is not running"
    echo "🚀 Starting SSH service..."
    sudo systemctl start ssh
    sudo systemctl enable ssh
    echo "✅ SSH service started and enabled"
else
    echo "✅ SSH is already running"
fi

# Check SSH configuration
echo ""
echo "📝 Checking SSH configuration..."

# Make sure password authentication is enabled (needed for web terminal)
if sudo grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config 2>/dev/null; then
    echo "⚠️  Password authentication is disabled"
    echo "🔧 Enabling password authentication..."
    sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sudo systemctl restart ssh
    echo "✅ Password authentication enabled"
fi

# Test SSH connection
echo ""
echo "🧪 Testing SSH connection..."
if timeout 5 ssh -o BatchMode=yes -o ConnectTimeout=5 localhost exit 2>/dev/null; then
    echo "✅ SSH connection successful (key-based)"
elif timeout 5 ssh -o PreferredAuthentications=password -o ConnectTimeout=5 localhost exit 2>/dev/null; then
    echo "✅ SSH connection successful (password-based)"
else
    echo "⚠️  SSH connection test failed"
    echo ""
    echo "You may need to:"
    echo "  1. Set a password for your user: sudo passwd $USER"
    echo "  2. Allow SSH connections: sudo ufw allow ssh"
    echo "  3. Check firewall settings"
fi

echo ""
echo "📊 SSH Status:"
sudo systemctl status ssh --no-pager -l

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Now restart ARC Connect and try the terminal again:"
echo "  cd /home/admin/ARC && ./start_arc_connect.sh"

