# OFAS - Offline Field Activity System
*Proof That the Surveyor Really Visited the Field*

## Project Summary

OFAS is an Android-based field visit verification system designed to prevent surveyors from faking their location and identity. It works completely offline using only the phone's built-in hardware, ensuring tamper-proof evidence of field visits through a combination of biometric verification, GPS/GNSS tracking, and cryptographic signing.

### Problem Statement
- **Current Issue**: 3 surveyors must visit 500 wheat fields, but they currently fake their location and identity
- **Requirement**: Create a system that proves a surveyor actually visited the field
- **Constraint**: Must work even in areas with no internet connectivity

### Core Verification Components

| Component | Purpose | Implementation |
|---|---|---|
| **WHO** | Verify surveyor identity | Selfie with blink detection, matched against saved face template |
| **WHERE** | Verify location | Phone GNSS (GPS/GLONASS/BeiDou/Galileo) matched against hidden location trail |
| **WHEN** | Verify timing | Satellite-derived time (never phone clock) recorded in tamper-proof trail |

## Key Features

### Anti-Cheating Mechanisms

- **Satellite Time Only**: The app never reads the phone's system clock, time zone, or EXIF date from photos. All timestamps come from GNSS satellites at the moment of capture.
- **Hidden Location Trail**: A background service records GNSS position, accuracy, and satellite time every 5 minutes in a hash-linked, cryptographically signed chain.
- **Photo Fingerprinting**: At shutter instant, each photo is locked with (satellite time + coordinates + SHA-256 fingerprint). Any post-capture edit breaks verification.
- **Liveness Detection**: Random blink challenges with in-app camera only. No gallery uploads permitted.
- **Trail Timeline Verification**: Each selfie and photo's timestamp must align with the continuous trail at that moment. Gaps are flagged.
- **Device Integrity**: Blocks rooted devices, developer options enabled, or fake/mock location apps.
- **Digital Signatures**: Each visit is signed with the phone's hardware-backed private key. Server verifies with the matching public key.
- **Offline-First Architecture**: All checks execute on-device. Visits are queued locally and auto-synced when internet returns.
- **Multi-Device Flexibility**: Any registered company phone can be used by any surveyor - all face templates are synced to every phone.

### User Roles

| Role | Permissions |
|---|---|
| **Super Admin** | Full control, can create admins, requires 2-person approval for sensitive actions, passkey support |
| **Admin** | Manage fields, surveyors, assignments, review visits (VALID/INVALID/FLAGGED), perform side-by-side comparisons |
| **Surveyor** | Field app - device check, face verification, field selection, photo capture (4-step flow) |

**Note**: Re-face check is required at each field visit for verification (selfie + blink challenge at every field).

### Field Visit Workflow

1. **Sync (Online)**: Download assigned fields for today + all surveyor face templates while connected to internet
2. **Device Check**: Verify airplane mode off, dev options off, location on, valid satellite fix
3. **Face Verification**: Take selfie, complete blink challenge, match against logged-in surveyor's saved face
4. **Select Field**: Choose from assigned fields for the day
5. **Capture Photos**: Take 3-10 photos of the field. Each photo is instantaneously stamped with GNSS time/location and fingerprinted
6. **Finish & Queue**: Visit is signed, encrypted, saved locally. Auto-uploads when connectivity returns

## Technical Architecture

### Mobile Application (Android)

| Component | Technology | Notes |
|---|---|---|
| **Language** | Kotlin (Recommended) | Type-safe, modern, excellent Android support |
| **UI Framework** | Jetpack Compose / XML Views | Keep minimal for surveyors |
| **Camera** | CameraX | In-app only, no gallery access |
| **Face Recognition** | TensorFlow Lite | Pre-trained model, compares live selfie with saved templates (not raw images) |
| **Local Database** | Room + SQLCipher | Encrypted storage for visits, trail, fields, faces |
| **Security** | Android Keystore | Hardware-backed private key storage |
| **Location** | Fused Location Provider + GNSS APIs | Must validate satellite fix, reject mock locations |
| **WorkManager** | For background trail + sync | Handles offline queuing and retry logic |

### Backend/Server (Python Flask)

| Component | Technology | Notes |
|---|---|---|
| **API Framework** | Python Flask (Flask-RESTX) | RESTful HTTPS API, modular blueprints for separation |
| **Database** | PostgreSQL + PostGIS | For field coordinates, distance calculations, geospatial queries |
| **Storage** | S3-compatible (MinIO/AWS S3) | Encrypted photo storage |
| **Authentication** | JWT + TOTP (MFA) | Argon2id password hashing, passkeys for Super Admins |
| **Crypto** | Python cryptography / libsodium | Signature verification, hash chaining |
| **Audit Logging** | Append-only hash-chained table | Tamper-evident, separate from main admin access |

### Backend Module Structure (Separate Files per Purpose)

| Module File | Purpose |
|---|---|
| `auth.py` | Authentication, JWT, TOTP, passkey handling, RBAC enforcement |
| `validation.py` | Data validation (visit payloads, field data, surveyor data, photo metadata) |
| `geospatial.py` | PostGIS distance calculations, field boundary checks, coordinate validation |
| `crypto.py` | Signature verification, hash chain validation, key management |
| `audit.py` | Append-only audit logging, chain integrity verification |
| `sync.py` | Sync endpoints (GET assigned fields + face templates, POST visit submission) |
| `admin.py` | Admin CRUD endpoints (fields, surveyors, phones, assignments) |
| `review.py` | Visit review endpoints (VALID/INVALID/FLAGGED, side-by-side comparison) |
| `models.py` | SQLAlchemy models (User, Surveyor, Field, Visit, TrailEntry, AuditLog, Phone) |
| `database.py` | Database connection, migrations (Alembic), session management |
| `config.py` | Configuration management (env vars, secrets, constants) |
| `app.py` | Flask application factory, blueprint registration, middleware |

### Data Security

- **Face Templates**: Stored as numeric embeddings (~2KB each), not images. Encrypted at rest.
- **Private Keys**: Generated and stored exclusively in Android Keystore, never exported
- **Visit Data**: AES-256 encrypted on device while queued
- **Trail Chain**: Each entry = (timestamp, lat/lon/acc, prevHash, signature). Tampering breaks chain
- **Photo Verification**: SHA-256 fingerprint rechecked on server
- **Audit Log**: Append-only, hash-chained, copied to storage admins cannot access

## Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **Android Version** | Android 12 | Android 14+ (4+ years security updates) |
| **GNSS** | GPS + GLONASS + BeiDou + Galileo | Same (L1+L5 dual-frequency bonus) |
| **RAM** | 4GB | 4-6GB |
| **Storage** | 64GB | 64GB (actual usage < 0.5GB typical) |
| **Rear Camera** | 13MP AF | 50MP AF (photos shrunk to ~500KB) |
| **Front Camera** | 5MP | 8MP+ (selfie & blink detection) |
| **Battery** | 4500mAh | 5000mAh + power bank |
| **Security** | Hardware-backed Keystore | Samsung Knox or equivalent |

**Pilot Recommendation:** Samsung Galaxy A06 (4GB/64GB) - ~Rs. 26,999

## Data Lifecycle & Storage Estimates

| Stage | Retention | Notes |
|---|---|---|
| **Phone (Local)** | Last 3 days of trail + max 300MB unsent visits | Visits auto-deleted after server confirms receipt |
| **Dashboard** | 12 months | Thumbnails + full photos for review |
| **Archive/Backup** | Compressed, encrypted, write-once | Checksum verified before deletion from dashboard |
| **Summary** | Forever | Aggregated totals only (tiny) |

**Annual Estimate (1000 fields, 10 surveyors, 6 photos/visit):** ~Live ~50-100GB, compressed backup ~30-60GB

## Implementation Plan

### Phase 1: Project Setup & Architecture (Week 1-2)
- [ ] **Project Initialization**: Create Android project with modular structure (app, core, data, security)
- [ ] **Dependencies**: Add CameraX, Room, SQLCipher, TensorFlow Lite, Location, Retrofit, WorkManager
- [ ] **Backend Setup**: Initialize API server, PostgreSQL + PostGIS, S3 storage
- [ ] **Database Design**: Schema for users, surveyors, fields, visits, trail_entries, audit_log, phones
- [ ] **API Contracts**: Define sync, submit, auth, admin endpoints
- [ ] **Encryption Strategy**: Plan key management, DB encryption, transit encryption

### Phase 2: Core Security & GNSS (Week 2-3)
- [ ] **Device Integrity**: Root detection, dev options check, mock location detection
- [ ] **GNSS Service**: Require fresh satellite fix with accuracy threshold, reject Wi-Fi/cell-only
- [ ] **Hidden Trail System**: Hash-linked chain implementation (prevHash = SHA256 of previous entry)
- [ ] **Key Management**: Generate EC/RSA keypair in Android Keystore, export public key to server
- [ ] **Background Trail**: Foreground service recording every 5 min (respect Android 14+ restrictions)
- [ ] **Trail Validation**: Chain continuity checks

### Phase 3: Face Recognition & Liveness (Week 3-4)
- [ ] **TFLite Integration**: Load face detection/embedding model
- [ ] **Face Templates**: Extract & encrypt embeddings (not images), store per surveyor
- [ ] **Face Matching**: Cosine similarity threshold against logged-in surveyor
- [ ] **Liveness Detection**: Blink detection via eye aspect ratio / challenge flow
- [ ] **In-App Camera**: CameraX with no gallery picker, front camera for selfie
- [ ] **Face Enrollment**: Admin flow to capture & template-ize surveyor face (1 photo at registration)

### Phase 4: Field Visit Flow (Week 4-5)
- [ ] **4-Step UI**: Device Check → Face Verify → Select Farm → Field Photos
- [ ] **Photo Capture**: On shutter, fetch latest GNSS fix (max age ~few seconds), compute hash, stamp
- [ ] **Trail Alignment**: Verify captured (time,loc) fits between trail entries ± tolerance
- [ ] **Field Validation**: Check distance from field center < allowed radius + accuracy constraints
- [ ] **Visit Assembly**: Bundle selfie, photos with their stamps, trail snapshot, surveyor+phone IDs
- [ ] **Signing**: Sign visit package with private key
- [ ] **Local Queue**: Store encrypted in Room+SQLCipher with status (QUEUED/SYNCING/SYNCED/FAILED)
- [ ] **Auto-Sync**: WorkManager triggered on connectivity change

### Phase 5: Admin Features (Week 5-6)
- [ ] **Authentication**: Login with username+password + TOTP, passkey for Super Admins
- [ ] **Field Management**: Add fields with center coords, radius, 3-10 reference photos
- [ ] **Surveyor Management**: Register with name/contact + face enrollment
- [ ] **Phone Management**: Register company phones, block lost phones, view phone status
- [ ] **Assignment**: Assign fields to surveyors (day-wise)
- [ ] **Visit Dashboard**: Filter by status (ALL/VALID/INVALID/FLAGGED), view details
- [ ] **Photo Comparison**: Side-by-side registered vs submitted with zoom/full view
- [ ] **Review Actions**: Mark same/not same with reason (logged to audit)
- [ ] **Audit Log**: View append-only log with chain integrity indicator

### Phase 6: Backend API & Sync (Week 6-7)
- [ ] **Sync Endpoint (GET)**: Return assigned fields + all faces (templates) for logged-in surveyor
- [ ] **Submit Endpoint (POST)**: Accept signed visit bundle with full verification
- [ ] **Signature Verification**: Verify visit signature against phone's public key
- [ ] **Trail Validation**: Reconstruct/check hash chain around visit timestamps
- [ ] **Photo Verification**: Recompute SHA-256, compare with submitted
- [ ] **Geospatial Check**: Server-side distance validation using PostGIS
- [ ] **Duplicate Prevention**: Visit ID uniqueness, timestamp sanity checks (not future, not too old)
- [ ] **RBAC**: Enforce role checks on all admin endpoints
- [ ] **Audit Logging**: Record all admin actions immutably

### Phase 7: Testing, Hardening & Pilot (Week 7-8)
- [ ] **Offline Testing**: Airplane mode, kill/restart mid-visit, battery die/resume
- [ ] **Anti-Cheat Testing**: Mock location attempt, trail tamper simulation, old gallery photo attempt
- [ ] **Edge Cases**: Poor GNSS under trees, weak signal, multi-day offline
- [ ] **Performance**: 8+ hour trail running, battery impact, DB size under caps
- [ ] **Security Review**: Keystore usage, SQLCipher, TLS config, input validation
- [ ] **Pilot Rollout**: 2 surveyors × 50 fields for 2 weeks, gather feedback
- [ ] **Fixes & Polish**: Error messages, help text

## Key Decisions Required

| Item | Status | Recommendation |
|---|---|---|
| **Re-face check at each field** | *Finalized* | Required at every field visit (selfie + blink challenge) |
| **Private install vs Play Store** | *Pending* | Private APK distribution (recommended) to avoid public exposure and easier control |
| **Trail interval (5 min)** | *Proposed* | 5 min balances battery vs granularity. Can tune after pilot |
| **Photo count (3-10)** | *Finalized* | Flexible range per visit |

## Implementation Notes

- **Never trust client**: All critical checks (signature, trail, distance, face match) must be re-verified server-side
- **Evidence immutability**: Visits, trail entries, audit log entries cannot be edited/deleted - only review marks added
- **Minimal UI for surveyors**: Hide all technical details (hashes, trail, keys). Show only "Verified" or "Try again"
- **Privacy**: Get written consent for face data. Trail only runs during app usage/context? (Spec says "during working hours" - clarify policy)
- **2-Person Rule**: Super Admin sensitive actions require second approval
- **Graceful Degradation**: Clear "Move to open ground" messages for poor GNSS, no silent failures
- **Battery**: Use efficient location requests, respect Doze mode, test 8+ hour runs

## Success Criteria

- [ ] Zero ability to submit visit without valid face+liveness match
- [ ] Satellite time exclusively used (verified via code audit)
- [ ] Trail chain breaks on any tampering attempt
- [ ] Works fully offline for multi-day scenario
- [ ] Photo edits/swaps detected via fingerprint mismatch
- [ ] Device integrity enforced on every app open
- [ ] All admin actions logged immutably
- [ ] Pilot shows < 5% false flags with honest surveyors

## Next Immediate Steps

1. **Stakeholder Review**: Get approval on pending decisions (especially re-face check per field)
2. **Technical Spec**: Write detailed spec for trail entry format, visit bundle structure, signing algorithm
3. **Library Selection**: Choose specific TFLite face model, validate SQLCipher integration
4. **Dev Environment**: Set up Android + backend repos with CI
5. **Proof-of-Concept**: Implement minimal trail + photo stamping on Android to validate GNSS timing
6. **Start Phase 1**: Initialize project structure as outlined
