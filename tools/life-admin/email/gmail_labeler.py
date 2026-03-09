#!/usr/bin/env python3
"""
Gmail Auto-Labeler — Life Admin Skill
Uses Claude to classify emails and apply Gmail labels automatically.

Setup:
  1. Enable Gmail API at console.cloud.google.com
  2. Create OAuth2 credentials → Download as credentials.json in this directory
  3. Set ANTHROPIC_API_KEY in .env or environment
  4. Run: python gmail_labeler.py --dry-run   (preview without applying labels)
  5. Run: python gmail_labeler.py              (apply labels)
"""

import os
import json
import argparse
import base64
from pathlib import Path
from dotenv import load_dotenv

import anthropic
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

load_dotenv(Path(__file__).parents[3] / ".env")

# ── Gmail OAuth scopes ────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# ── Label definitions ─────────────────────────────────────────────────────────
# Each label maps to a Gmail label that will be created if it doesn't exist.
# Format: Gmail label name → description used in the Claude prompt
LABELS = {
    "Life/Bills & Finance":    "utility bills, bank statements, credit card, mortgage, rent, insurance payments, tax documents",
    "Life/Receipts & Orders":  "purchase receipts, order confirmations, shipping notifications, delivery updates",
    "Life/Newsletters":        "newsletters, marketing emails, promotional offers, subscription digests, product announcements",
    "Life/Family & Friends":   "personal emails from family or friends, social invitations, event planning with people you know",
    "Life/Travel":             "flight confirmations, hotel reservations, car rentals, itineraries, travel deals",
    "Life/Health & Medical":   "doctor appointments, pharmacy, insurance claims, lab results, health reminders",
    "Life/Government & Legal": "government agencies, IRS, DMV, legal notices, court documents, official forms",
    "Life/Work":               "work-related emails, colleagues, clients, job applications, professional services",
    "Life/Subscriptions":      "software subscriptions, streaming services, SaaS renewals, app notifications",
    "Life/Events":             "event invitations, ticket confirmations, RSVPs, school events, community activities",
}

CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"
TOKEN_PATH = Path(__file__).parent / "token.json"

# ── Gmail auth ────────────────────────────────────────────────────────────────

def get_gmail_service():
    """Authenticate and return a Gmail API service object."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"Gmail credentials not found at {CREDENTIALS_PATH}\n"
                    "Download OAuth2 credentials from console.cloud.google.com and "
                    "save as credentials.json in the email/ directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ── Gmail label management ────────────────────────────────────────────────────

def get_or_create_label(service, label_name: str) -> str:
    """Return the Gmail label ID, creating the label if it doesn't exist."""
    existing = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in existing:
        if label["name"] == label_name:
            return label["id"]

    # Create nested label (Gmail supports / as separator)
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        },
    ).execute()
    print(f"  Created label: {label_name}")
    return new_label["id"]


def ensure_labels_exist(service) -> dict[str, str]:
    """Return a mapping of label_name → label_id, creating any that are missing."""
    return {name: get_or_create_label(service, name) for name in LABELS}


# ── Email fetching ────────────────────────────────────────────────────────────

def fetch_unlabeled_emails(service, max_results: int = 50) -> list[dict]:
    """Fetch recent emails that haven't been labeled by this tool yet."""
    query = "-label:Life/Bills-Finance -label:Life/Receipts-Orders -label:Life/Newsletters "
    query += "-label:Life/Family-Friends -label:Life/Travel -label:Life/Health-Medical "
    query += "-label:Life/Government-Legal -label:Life/Work -label:Life/Subscriptions "
    query += "-label:Life/Events in:inbox"

    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    ).execute()

    messages = result.get("messages", [])
    emails = []
    for msg in messages:
        full = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        snippet = full.get("snippet", "")
        emails.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": snippet[:300],
        })
    return emails


# ── Claude classification ─────────────────────────────────────────────────────

def classify_emails(emails: list[dict]) -> list[dict]:
    """
    Use Claude to classify a batch of emails into labels.
    Returns the same list with a 'label' key added to each email.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    label_descriptions = "\n".join(
        f'- "{name}": {desc}' for name, desc in LABELS.items()
    )

    email_batch = "\n\n".join(
        f"[{i+1}] From: {e['from']}\nSubject: {e['subject']}\nSnippet: {e['snippet']}"
        for i, e in enumerate(emails)
    )

    prompt = f"""You are an email classifier for a personal life admin system.

Classify each email below into exactly one of these labels:
{label_descriptions}

If an email doesn't fit any label, respond with "skip" for that email.

Emails to classify:
{email_batch}

Respond with a JSON array of objects, one per email, in the same order:
[
  {{"index": 1, "label": "Life/Bills & Finance", "reason": "utility bill"}},
  {{"index": 2, "label": "skip", "reason": "unclear category"}},
  ...
]

Return only the JSON array, no other text."""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response_text = stream.get_final_message().content[0].text

    results = json.loads(response_text)
    for res in results:
        idx = res["index"] - 1
        if 0 <= idx < len(emails):
            emails[idx]["label"] = res["label"]
            emails[idx]["reason"] = res.get("reason", "")

    return emails


# ── Label application ─────────────────────────────────────────────────────────

def apply_label(service, email_id: str, label_id: str):
    """Add a label to a Gmail message."""
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"addLabelIds": [label_id]},
    ).execute()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Auto-label Gmail with Claude")
    parser.add_argument("--dry-run", action="store_true", help="Preview labels without applying")
    parser.add_argument("--max", type=int, default=50, help="Max emails to process (default: 50)")
    parser.add_argument("--batch-size", type=int, default=20, help="Claude batch size (default: 20)")
    args = parser.parse_args()

    print("Authenticating with Gmail...")
    service = get_gmail_service()

    if not args.dry_run:
        print("Ensuring Gmail labels exist...")
        label_map = ensure_labels_exist(service)
    else:
        label_map = {name: "dry-run-id" for name in LABELS}

    print(f"Fetching up to {args.max} unlabeled inbox emails...")
    emails = fetch_unlabeled_emails(service, max_results=args.max)

    if not emails:
        print("No unlabeled emails found.")
        return

    print(f"Found {len(emails)} emails. Classifying in batches of {args.batch_size}...")

    labeled = skipped = errors = 0

    for i in range(0, len(emails), args.batch_size):
        batch = emails[i : i + args.batch_size]
        print(f"\nBatch {i // args.batch_size + 1}: classifying {len(batch)} emails...")

        try:
            classified = classify_emails(batch)
        except Exception as e:
            print(f"  Classification error: {e}")
            errors += len(batch)
            continue

        for email in classified:
            label = email.get("label", "skip")
            reason = email.get("reason", "")
            subject = email["subject"][:60]

            if label == "skip" or label not in LABELS:
                print(f"  SKIP  | {subject}")
                skipped += 1
                continue

            print(f"  {'DRY ' if args.dry_run else ''}LABEL | {label:<35} | {subject}")

            if not args.dry_run:
                try:
                    apply_label(service, email["id"], label_map[label])
                    labeled += 1
                except Exception as e:
                    print(f"         Error applying label: {e}")
                    errors += 1
            else:
                labeled += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done.")
    print(f"  Labeled:  {labeled}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")

    if args.dry_run:
        print("\nRun without --dry-run to apply labels.")


if __name__ == "__main__":
    main()
