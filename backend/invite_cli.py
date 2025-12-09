#!/usr/bin/env python3
"""CLI tool for generating Ed25519 keypairs and invite tokens."""

import argparse
import sys
import uuid
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import jwt


def generate_keypair():
    """Generate a new Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    return private_pem, public_pem


def create_invite_token(private_key_pem: str, note: str = "") -> str:
    """Create a signed invite token."""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    
    payload = {
        "jti": str(uuid.uuid4()),  # Unique token ID
        "iat": int(datetime.utcnow().timestamp()),
        "type": "invite",
    }
    if note:
        payload["note"] = note
    
    token = jwt.encode(payload, private_key, algorithm="EdDSA")
    return token


def main():
    parser = argparse.ArgumentParser(description="Invite token management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate keypair command
    gen_parser = subparsers.add_parser("generate-keys", help="Generate new Ed25519 keypair")
    gen_parser.add_argument("--output", "-o", help="Output file prefix (creates PREFIX.key and PREFIX.pub)")
    
    # Create token command
    token_parser = subparsers.add_parser("create-token", help="Create a new invite token")
    token_parser.add_argument("--key", "-k", required=True, help="Path to private key file")
    token_parser.add_argument("--note", "-n", default="", help="Optional note/identifier for this invite")
    
    args = parser.parse_args()
    
    if args.command == "generate-keys":
        private_pem, public_pem = generate_keypair()
        
        if args.output:
            with open(f"{args.output}.key", "w") as f:
                f.write(private_pem)
            with open(f"{args.output}.pub", "w") as f:
                f.write(public_pem)
            print(f"Keys written to {args.output}.key and {args.output}.pub")
            print(f"\nAdd this to your .env file:")
            # Escape newlines for env file
            escaped_pub = public_pem.replace("\n", "\\n")
            print(f'INVITE_PUBLIC_KEY="{escaped_pub}"')
        else:
            print("=== PRIVATE KEY (keep secret!) ===")
            print(private_pem)
            print("=== PUBLIC KEY (add to .env) ===")
            print(public_pem)
            print("\n=== For .env file ===")
            escaped_pub = public_pem.replace("\n", "\\n")
            print(f'INVITE_PUBLIC_KEY="{escaped_pub}"')
    
    elif args.command == "create-token":
        try:
            with open(args.key, "r") as f:
                private_key_pem = f.read()
        except FileNotFoundError:
            print(f"Error: Key file not found: {args.key}", file=sys.stderr)
            sys.exit(1)
        
        token = create_invite_token(private_key_pem, args.note)
        print(token)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

