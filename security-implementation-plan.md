# End-to-End Per-User Image Encryption

## Background

The system stores sensitive medical images (uploaded radiological scans + GradCAM overlays) as plaintext base64 strings in the SQLite `analysis_history` table and within the `results` JSON blob. Anyone with read access to the database file can view every patient's medical image.

The goal is to make those images **readable only by the user who owns them**, using modern authenticated encryption, while keeping the frontend experience identical.

---

## Cryptographic Design

### Threat model
- **Threat**: Database file (or cloud backup) is exfiltrated by an attacker, a rogue admin, or a compromised cloud provider.
- **Not in scope**: A logged-in user whose session is hijacked (that is a session-security concern, not a storage-encryption concern).

### Chosen scheme: AES-256-GCM (symmetric, per-user key, password-derived)

| Property | Choice | Rationale |
|---|---|---|
| Encryption | AES-256-GCM | NIST-standard, authenticated, fast, widely available in Python's `cryptography` library |
| Key derivation | Argon2id (via `argon2-cffi`) | Winner of the Password Hashing Competition; memory-hard, resistant to GPU/ASIC brute-force |
| Per-user salt | 16 random bytes, stored in `users.encryption_salt` | Unique salt ⇒ unique key per user even if two users share a password |
| Per-ciphertext nonce | 12 random bytes, prepended to ciphertext blob | AES-GCM nonce; unique per encryption operation |
| Authentication tag | 16 bytes (GCM default) | Integrity + authenticity verified on decryption |

**Key derivation**: `user_key = Argon2id(password, salt, time=2, memory=65536, threads=2, key_len=32)`

The user's plaintext password is the *only* input to key derivation. The backend **never stores the encryption key** — it is re-derived at request time from the credentials the user just sent.

> [!IMPORTANT]
> **Key lifetime**: The derived key exists only in memory for the duration of a single request. It is never written to disk, logged, or placed in the JWT.

### Why not asymmetric (RSA/ECIES)?
- Asymmetric would require storing a private key server-side (defeating the threat model) or in the client browser (complex, fragile). AES-GCM with a password-derived key gives the same "only the user can decrypt" guarantee without the complexity.

### Data encrypted
| Field | Encrypted? |
|---|---|
| `analysis_history.image_base64` | ✅ AES-256-GCM ciphertext, base64-encoded |
| `results.gradcam_base64` (inside the `results` JSON) | ✅ same scheme |
| `results` (other fields: confidence, status, model_name, etc.) | ❌ plain JSON — no sensitive image data |
| `users.*` | ❌ unchanged (password already hashed with bcrypt) |

---

## Proposed Changes

### New dependency

#### [MODIFY] [pyproject.toml](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/pyproject.toml)
Add `cryptography>=42.0.0` and `argon2-cffi>=23.1.0`.  
`cryptography` is already a transitive dep of `python-jose`; we make it explicit. `argon2-cffi` is new.

---

### New module — encryption service

#### [NEW] `app/services/encryption.py`
Pure utility module; no FastAPI or DB imports.

```
EncryptionService
├── derive_key(password: str, salt: bytes) -> bytes        # Argon2id KDF
├── encrypt(plaintext: str, key: bytes) -> str             # AES-256-GCM → base64 blob
├── decrypt(ciphertext: str, key: bytes) -> str            # inverse
└── generate_salt() -> bytes                               # os.urandom(16)
```

The `encrypt()` output format is: `base64( nonce[12] || tag[16] || ciphertext )`.  
This self-contained blob is stored verbatim in the DB column.

---

### Database schema changes

#### [MODIFY] [database.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/models/database.py)

1. **`users` table** — add column `encryption_salt TEXT` (hex-encoded 16-byte random salt, generated once at account creation, never changed).
2. **Schema migration** — `_init_database()` will `ALTER TABLE` to add the salt column if absent (backward-compat with existing rows; existing users get a salt assigned on first login).
3. **New helper** `get_user_encryption_salt(user_id) -> Optional[str]` and `set_user_encryption_salt(user_id, salt_hex)`.

---

### Auth service — salt lifecycle

#### [MODIFY] [services/auth.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/services/auth.py)

- `create_user(...)` → after `db.create_user(...)`, generate salt and store it.
- `authenticate_user(email, password)` → after successful bcrypt check, derive the AES key, return it alongside the user dict (only in memory, never serialized).
- New helper: `get_encryption_key(user_id, password) -> Optional[bytes]`.

> [!WARNING]
> **Password change caveat**: If a user changes their password the encryption key changes, making all existing ciphertext unreadable. The `change_password` flow must:
> 1. Re-derive the old key from `current_password`.
> 2. Decrypt all the user's `image_base64` and `gradcam_base64` fields with the old key.
> 3. Re-encrypt them with the new key.
> 4. Store the new `password_hash` atomically.
>
> This is implemented in `AuthService.change_password()`.

---

### Queue service — encrypt on write, decrypt on read

#### [MODIFY] [services/queue_service.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/services/queue_service.py)

- `submit_analysis(...)` receives the user's plaintext `password` (passed from the API layer).
- Before calling `db.add_analysis_history(...)`, encrypts `image_base64` using the derived key.
- `_process_analysis_task(...)`: after the model returns `results`, extracts `gradcam_base64`, encrypts it, and stores the modified `results` dict.

---

### Analyze API — thread the password through

#### [MODIFY] [api/analyze.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/api/analyze.py)

The current `/analyze/xray` and `/analyze/ct` endpoints accept a Bearer token. We need the user's **password** to derive the encryption key. Two options:

> [!IMPORTANT]
> **Design decision — how to pass the password to the encryption layer**
>
> **Option A — Password in request body (recommended)**  
> The frontend sends `password` as an additional form field alongside the image upload. The password is transmitted over HTTPS (already required) and used only in-process to derive the key.
>
> **Option B — Password encrypted in JWT claims**  
> Store an encrypted form of the password in the JWT at login time. Complex, and if the JWT key leaks the user password leaks too.
>
> **Option C — Short-lived per-session encrypted key**  
> On login, derive the key and store it server-side in an in-memory session cache keyed by `user_id`. The key lives in RAM and is evicted at logout or expiry. No password re-entry needed; works with the existing token flow.
>
> Option C is the most transparent to the frontend (no API change, no password re-entry) and is the **recommended approach**. The session cache is a `dict[user_id -> (key_bytes, expires_at)]` protected by a threading lock.

**Chosen: Option C** — session key cache.

- `AuthService.authenticate_user()` derives and caches the key.
- `AuthService.logout_user(user_id)` evicts the key.
- The analyze endpoints call `auth_service.get_cached_key(user_id)` to retrieve the key.
- Cache TTL equals `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min); expired keys are evicted lazily.

---

### Auth API — cache on login, evict on logout

#### [MODIFY] [api/auth.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/api/auth.py)

- `/auth/login` — after issuing the JWT, call `auth_service.cache_encryption_key(user_id, password)`.
- New endpoint `POST /auth/logout` — evicts the cached key for that user.
- `/auth/history` — when returning history entries that include `image_base64`, decrypt them before serialization using the cached key.

---

### History decryption on read

#### [MODIFY] [models/database.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/models/database.py)

`get_user_history()` returns raw encrypted blobs. Decryption happens in the API / service layer (not in the DB model), keeping the DB layer free of crypto logic.

#### [MODIFY] [api/auth.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/api/auth.py)

The `GET /auth/history` handler decrypts `image_base64` and `results.gradcam_base64` fields before returning the response.

---

### Status endpoint decryption

#### [MODIFY] [api/analyze.py](file:///home/skandabhairava/Desktop/medical-deepfake-website/backend/app/api/analyze.py)

`GET /analyze/status/{history_id}` — when status is `completed`, the `results` field contains encrypted `gradcam_base64`. Decrypt before returning.

---

### Migration of existing data

#### [NEW] `app/utils/migrate_encryption.py`

A one-shot migration script that:
1. For each user, generates a new `encryption_salt` (stored in DB).
2. For all their `analysis_history` rows that have plaintext `image_base64` / `gradcam_base64`: **marks them as `[LEGACY_UNENCRYPTED]`** — a sentinel prefix that the decryption layer recognizes as plaintext pass-through.

> [!CAUTION]
> The migration cannot encrypt existing data because we do not store user passwords. Existing image data will remain readable (with `[LEGACY_UNENCRYPTED]` prefix passthrough) until the user re-uploads. This is documented behavior — the alternative (deleting existing image blobs) is offered as a stricter option.

---

## File Change Summary

| File | Action | What changes |
|---|---|---|
| `pyproject.toml` | MODIFY | Add `cryptography`, `argon2-cffi` |
| `app/services/encryption.py` | **NEW** | AES-256-GCM + Argon2id KDF utilities |
| `app/models/database.py` | MODIFY | `encryption_salt` column; salt helpers; migration in `_init_database` |
| `app/services/auth.py` | MODIFY | Salt generation on create; key derivation + in-memory cache on login; key eviction on logout; re-encrypt on password change |
| `app/api/auth.py` | MODIFY | Cache key on login; new logout endpoint; decrypt history on read |
| `app/services/queue_service.py` | MODIFY | Encrypt `image_base64` before DB write; encrypt `gradcam_base64` after model runs |
| `app/api/analyze.py` | MODIFY | Decrypt `gradcam_base64` in status response |
| `app/utils/migrate_encryption.py` | **NEW** | One-shot migration: add salts + mark legacy rows |

**Frontend: zero changes.** The API contract is identical — `image_base64` and `gradcam_base64` are still plain base64 strings from the frontend's perspective; decryption is transparent server-side.

---

## Verification Plan

### Automated Tests
- Unit-test `EncryptionService`: round-trip encrypt/decrypt, wrong-key rejection, tampered-ciphertext GCM tag failure.
- Integration-test login → submit analysis → get history (check `image_base64` is decrypted in response, encrypted in DB).

### Manual Verification
- After implementation, inspect the SQLite DB directly (`sqlite3 medical_deepfake.db "SELECT image_base64 FROM analysis_history LIMIT 1"`) to confirm the stored blob is unintelligible ciphertext.
- Confirm the frontend history page and GradCAM images render correctly.

---

## Open Questions

> [!IMPORTANT]
> **Q1**: Should the `change_password` flow silently re-encrypt all existing images (could be slow for users with many analyses) or should it warn the user that existing history images will need to be re-uploaded? Which do you prefer?

> [!IMPORTANT]
> **Q2**: For existing users' historical data (images stored before this change), should we:
> - **(A) Keep as passthrough** — existing images remain viewable but unencrypted in the DB (with a `LEGACY:` prefix flag so the decryption layer knows to pass them through)
> - **(B) Delete existing `image_base64` blobs** — existing history entries lose their image preview; only new uploads are encrypted
> - **(C) Prompt users to re-upload** — not really feasible in the UI

> [!NOTE]
> **Q3**: The session key cache currently lives in application memory. If the backend is restarted (e.g., during deployment), users need to log in again to refresh the cache — which they would do anyway since their JWT also becomes invalid after SECRET_KEY changes. This is acceptable behavior; just confirming.
