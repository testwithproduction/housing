# Security Policy

## Security Features

This desktop application implements several security measures:

### Electron Security
- **Context Isolation**: Enabled to prevent renderer access to Node.js APIs
- **Node Integration**: Disabled in renderer process
- **Web Security**: Enabled to prevent loading of insecure content
- **DevTools**: Only available in development mode
- **Preload Script**: Secure communication between main and renderer processes
- **Navigation Control**: Blocks navigation to external URLs (opens in system browser)
- **Download Restrictions**: Only allows downloads from the local Streamlit server

### Network Security
- **Localhost Only**: Application only connects to localhost Streamlit server
- **Port Validation**: Automatic port detection with fallback to secure defaults
- **External Link Handling**: All external links open in system browser, not in app

### Process Security
- **Sandboxing**: Renderer process runs with restricted permissions
- **Resource Isolation**: Python process runs separately from Electron
- **Clean Shutdown**: Proper cleanup of all processes on exit

## Security Best Practices

### For Developers
1. **Keep Dependencies Updated**: Run `npm audit` regularly
2. **Review Code Changes**: All security-related changes should be reviewed
3. **Test Security Features**: Verify navigation blocks and download restrictions
4. **Monitor for Vulnerabilities**: Use `npm audit` and security scanners

### For Users
1. **Download from Trusted Sources**: Only install from official releases
2. **Verify Checksums**: Check file integrity before installation
3. **Keep Updated**: Install security updates promptly
4. **Firewall Configuration**: Allow only localhost connections

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email security concerns to: [your-security-email]
3. Include detailed reproduction steps
4. Allow time for investigation and patching

## Security Checklist

Before each release:
- [ ] Run `npm audit` and fix all high/critical issues
- [ ] Test navigation restrictions
- [ ] Verify external links open in system browser
- [ ] Check download restrictions work properly
- [ ] Validate that DevTools are disabled in production
- [ ] Confirm all processes shut down cleanly

## Known Security Considerations

1. **Python Dependencies**: The app relies on Python packages which may have their own vulnerabilities
2. **Streamlit Framework**: Security depends on Streamlit's built-in protections
3. **Local Network**: App binds to localhost only, but other local processes could potentially access it
4. **File Access**: Python process has file system access within user permissions

## Updates and Patching

- Security updates will be released as soon as possible
- Users will be notified through GitHub releases
- Critical security fixes may be backported to older versions

## Compliance

This application follows:
- OWASP Electron Security Guidelines
- Node.js Security Best Practices
- Python Security Recommendations