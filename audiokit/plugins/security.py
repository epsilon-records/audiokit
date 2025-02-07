import hashlib
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class PluginVerificationError(Exception):
    """Exception raised for plugin verification failures"""

class PluginVerifier:
    def __init__(self, public_key_path: Path = Path("~/.audiokit/keys/public.pem")):
        self.public_key = self._load_public_key(public_key_path.expanduser())

    def verify_plugin(self, plugin_path: Path) -> bool:
        """Verify plugin signature and checksum"""
        if not plugin_path.with_suffix('.sig').exists():
            raise PluginVerificationError("Missing signature file")
            
        return (
            self._verify_signature(plugin_path) and 
            self._verify_checksum(plugin_path)
        )

    def _verify_signature(self, plugin_path: Path) -> bool:
        """Verify cryptographic signature"""
        sig_path = plugin_path.with_suffix('.sig')
        try:
            with open(plugin_path, "rb") as f:
                plugin_data = f.read()
                
            with open(sig_path, "rb") as f:
                signature = f.read()

            self.public_key.verify(
                signature,
                plugin_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except FileNotFoundError:
            return False

    def _verify_checksum(self, plugin_path: Path) -> bool:
        """Verify file integrity checksum"""
        checksum_path = plugin_path.with_suffix('.sha256')
        if not checksum_path.exists():
            return False
            
        with open(plugin_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            
        with open(checksum_path) as f:
            stored_hash = f.read().strip()
            
        return file_hash == stored_hash

    def _load_public_key(self, path: Path):
        """Load public key from file"""
        if not path.exists():
            raise PluginVerificationError("Missing public key for verification")
            
        with open(path, "rb") as key_file:
            return load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            ) 