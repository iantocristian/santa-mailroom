#!/usr/bin/env python3
"""CLI tool for generating short invite codes."""

import argparse
import sys
import secrets
import string
from datetime import datetime, timedelta

# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import InviteCode


def generate_code() -> str:
    """Generate a short invite code like SANTA-XK7M2P."""
    chars = string.ascii_uppercase + string.digits
    # Exclude confusing characters
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    random_part = ''.join(secrets.choice(chars) for _ in range(6))
    return f"SANTA-{random_part}"


def create_invite(note: str = "", expires_days: int = None) -> str:
    """Create a new invite code and store it in the database."""
    db = SessionLocal()
    try:
        # Generate unique code
        while True:
            code = generate_code()
            existing = db.query(InviteCode).filter(InviteCode.code == code).first()
            if not existing:
                break
        
        # Create invite
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        invite = InviteCode(
            code=code,
            note=note if note else None,
            expires_at=expires_at
        )
        db.add(invite)
        db.commit()
        
        return code
    finally:
        db.close()


def list_invites(show_used: bool = False):
    """List all invite codes."""
    db = SessionLocal()
    try:
        query = db.query(InviteCode)
        if not show_used:
            query = query.filter(InviteCode.used_at.is_(None), InviteCode.is_active == True)
        
        invites = query.order_by(InviteCode.created_at.desc()).all()
        
        print(f"{'Code':<15} {'Note':<20} {'Created':<12} {'Status':<10}")
        print("-" * 60)
        
        for invite in invites:
            created = invite.created_at.strftime("%Y-%m-%d") if invite.created_at else "N/A"
            
            if invite.used_at:
                status = "Used"
            elif not invite.is_active:
                status = "Disabled"
            elif invite.expires_at and invite.expires_at < datetime.utcnow():
                status = "Expired"
            else:
                status = "Active"
            
            note = (invite.note[:17] + "...") if invite.note and len(invite.note) > 20 else (invite.note or "")
            print(f"{invite.code:<15} {note:<20} {created:<12} {status:<10}")
        
        if not invites:
            print("No invite codes found.")
    finally:
        db.close()


def revoke_invite(code: str):
    """Revoke an invite code."""
    db = SessionLocal()
    try:
        invite = db.query(InviteCode).filter(InviteCode.code == code).first()
        if not invite:
            print(f"Error: Invite code '{code}' not found.", file=sys.stderr)
            return False
        
        if invite.used_at:
            print(f"Warning: This code has already been used.", file=sys.stderr)
        
        invite.is_active = False
        db.commit()
        print(f"Revoked: {code}")
        return True
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Invite code management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create invite command
    create_parser = subparsers.add_parser("create", help="Create a new invite code")
    create_parser.add_argument("--note", "-n", default="", help="Optional note about who this is for")
    create_parser.add_argument("--expires", "-e", type=int, help="Days until expiry (optional)")
    create_parser.add_argument("--count", "-c", type=int, default=1, help="Number of codes to create")
    
    # List invites command
    list_parser = subparsers.add_parser("list", help="List invite codes")
    list_parser.add_argument("--all", "-a", action="store_true", help="Show used/expired codes too")
    
    # Revoke invite command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an invite code")
    revoke_parser.add_argument("code", help="The invite code to revoke")
    
    args = parser.parse_args()
    
    if args.command == "create":
        for i in range(args.count):
            code = create_invite(args.note, args.expires)
            print(code)
    
    elif args.command == "list":
        list_invites(show_used=args.all)
    
    elif args.command == "revoke":
        revoke_invite(args.code)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
