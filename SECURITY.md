# Security Policy

## Security Features

pwick is designed with security as the top priority. This document outlines the security features and practices implemented in the application.

### Encryption

**Algorithm**: AES-256-GCM (Advanced Encryption Standard with Galois/Counter Mode)
- 256-bit key size (highest security level)
- Authenticated encryption (prevents tampering)
- 96-bit random nonce per encryption operation
- AEAD (Authenticated Encryption with Associated Data)

**Why AES-256-GCM?**
- Industry standard, widely vetted
- Provides both confidentiality and authenticity
- Prevents tampering and modification attacks
- Fast and efficient on modern hardware

### Key Derivation

**Function**: Argon2id
- Winner of the Password Hashing Competition (2015)
- Resistant to GPU/ASIC attacks
- Memory-hard function

**Parameters**:
- Time cost: 3 iterations
- Memory cost: 65536 KB (64 MB)
- Parallelism: 1 thread
- Salt: 16 random bytes (unique per vault)
- Output: 32 bytes (256 bits for AES-256)

**Why Argon2id?**
- Best-in-class defense against brute-force attacks
- Requires significant memory, preventing parallel attacks
- Adjustable parameters for future-proofing
- Recommended by OWASP and security experts

### Data Protection

1. **Master Password**
   - Never stored on disk (not even hashed)
   - Only exists in memory during vault unlock
   - Cleared from memory when vault is locked

2. **Vault File**
   - Entire contents encrypted as a single blob
   - Metadata and all entries encrypted together
   - No plaintext data in the file

3. **Random Generation**
   - Uses `os.urandom()` for cryptographic randomness
   - Secure salt generation
   - Secure nonce generation
   - Strong password generation with `secrets` module

### Threat Model

**Protected Against**:
- ✓ Brute-force password attacks (Argon2id makes this computationally expensive)
- ✓ Dictionary attacks (strong KDF)
- ✓ Data tampering (authenticated encryption)
- ✓ Data theft (file is encrypted at rest)
- ✓ Plaintext leakage (no plaintext stored)
- ✓ Rainbow table attacks (unique salt per vault)

**NOT Protected Against**:
- ✗ Weak master passwords (user responsibility)
- ✗ Keyloggers on compromised systems
- ✗ Screen capture on compromised systems
- ✗ Memory dumps while vault is unlocked
- ✗ Physical access to running system

### Privacy Features

**No Network Activity**:
- Zero network connections
- No cloud sync
- No analytics or telemetry
- No automatic updates
- No external API calls

**Local-Only Storage**:
- Vault file location controlled by user
- No temporary files with sensitive data
- No swap file protection (user responsibility)

### Best Practices for Users

#### Master Password
1. **Use a strong, unique password**
   - Minimum 12 characters
   - Mix uppercase, lowercase, numbers, symbols
   - Avoid dictionary words
   - Use a passphrase for memorability

2. **Store it safely**
   - Write it down physically in a secure location
   - Don't store it in a text file
   - Don't share it via email or messaging
   - Consider a physical backup in a safe

3. **Recovery is impossible**
   - There is NO password recovery mechanism
   - If you forget it, your data is lost forever
   - This is by design for security

#### Vault File Management
1. **Regular backups**
   - Use the Export function regularly
   - Store encrypted exports in multiple locations
   - USB drives, encrypted cloud storage, etc.

2. **File permissions** (Linux/Mac)
   ```bash
   chmod 600 myvault.vault  # Owner read/write only
   ```

3. **Secure deletion**
   - When deleting old vaults, use secure deletion tools
   - On Linux: `shred -u oldvault.vault`
   - On Windows: Use SDelete or similar tools

#### Usage Habits
1. **Lock when idle**
   - Always lock the vault when stepping away
   - Close the application when not in use

2. **Trusted systems only**
   - Only use pwick on systems you trust
   - Avoid public or shared computers
   - Be aware of screen sharing/recording

3. **Password hygiene**
   - Use the password generator for new accounts
   - Don't reuse passwords across services
   - Update passwords periodically

### Code Security

**Dependencies**:
All dependencies are from trusted, well-maintained projects:
- PyQt5: Official Qt bindings for Python
- cryptography: Maintained by the Python Cryptographic Authority
- argon2-cffi: Official Python bindings for Argon2
- pyperclip: Simple clipboard library

**Regular Updates**:
Dependencies should be updated regularly for security patches:
```bash
pip install --upgrade -r requirements.txt
```

### Audit and Review

**Code Review**:
- All code is open source and available for review
- Cryptographic implementations use standard libraries
- No custom crypto (use well-vetted implementations)

**Security Testing**:
- Unit tests for all crypto functions
- Integration tests for complete workflows
- CodeQL static analysis for vulnerability detection

### Reporting Security Issues

If you discover a security vulnerability in pwick:

1. **DO NOT** create a public GitHub issue
2. Email the maintainer directly (see GitHub profile)
3. Provide details:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work to address the issue promptly.

### Security Changelog

**Version 1.0.0**:
- Initial release with AES-256-GCM + Argon2id
- No known vulnerabilities
- CodeQL analysis: 0 alerts

### Future Security Considerations

**Planned Improvements**:
- [ ] Optional hardware security key support (YubiKey)
- [ ] Optional 2FA for vault unlock
- [ ] Secure memory wiping on exit
- [ ] Vault file integrity verification
- [ ] Auto-lock after inactivity timeout

**Not Planned** (by design):
- Cloud sync (would require network, server)
- Password sharing (increases attack surface)
- Browser integration (would require extensions)
- Mobile versions (would require different security model)

### Compliance and Standards

**Follows**:
- OWASP Password Storage Guidelines
- NIST SP 800-63B Digital Identity Guidelines
- RFC 9106 (Argon2)
- FIPS 197 (AES)

**Suitable For**:
- Personal password management
- Small team password sharing (via encrypted export)
- Air-gapped systems
- High-security environments

**NOT Suitable For**:
- Enterprise password management (use dedicated solutions)
- Automated systems (no API)
- Compliance requiring audit logs (no logging)

---

For more information, see:
- [README.md](README.md) - General documentation
- [TESTING.md](TESTING.md) - Security testing procedures
- [QUICKREF.md](QUICKREF.md) - Usage reference

Last updated: October 2025
