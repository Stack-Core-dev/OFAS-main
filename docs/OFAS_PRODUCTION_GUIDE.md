# OFAS Production Guide

OFAS (Offline Field Activity System) verifies that a surveyor physically visited
an assigned farm. The Android application works without mobile data while a
surveyor is in the field. It records GNSS evidence, identity confirmation,
photos, timestamps, and a signed trail. The backend stores the evidence and the
admin application provides assignment, review, audit, and reporting workflows.

## 1. Product rules

### Roles

- **Surveyor**: uses the Android application, sees only assigned active fields,
  verifies identity, records visits, and queues evidence offline.
- **Admin**: manages fields, surveyors, phones, assignments, and visit review.
- **Super admin**: manages users and security-sensitive administration.

### Administrator account management

The React dashboard's **Users** tab lists administrator and super administrator
accounts. Super administrators can edit an account email address or deactivate
an account. Deactivation is soft: the user record and audit history remain
available, but the account can no longer authenticate. A super administrator
cannot deactivate their own active session.

### Creating surveyor accounts

Admins create surveyors from the React dashboard's **Users** tab. A surveyor
account requires an employee ID, full name, phone number, and a strong
password; an email address is not requested. The backend creates the matching
`surveyor` login account and stores only the Argon2 password hash. When the
legacy non-null user email column requires a value, OFAS generates an internal
`<employee-id>@ofas.local` identifier rather than asking the admin for email.

### Managing assignments

Admins use the React dashboard's **Assignments** tab to assign an active field
to an active surveyor for a date range. The admin creates this assignment once;
the surveyor can visit the field on any day within the range. The tab loads
existing assignments from the backend and displays the surveyor, field, date
range, and completion status. The backend rejects missing resources, duplicate
assignments, and invalid ranges.

### Surveyor workflow

1. The device is enrolled while online with username/password and any required
   TOTP challenge.
2. The Android app downloads the surveyor's assignments.
3. Later app launches use simple local device verification.
4. Before a visit, the device checks location permission, device integrity, and
   GNSS availability.
5. A foreground service records a signed location trail at the configured
   interval.
6. The surveyor selects an assigned field and completes simple identity
   confirmation.
7. Photos are captured in-app, stamped with GNSS evidence, hashed, and added to
   an immutable visit bundle.
8. The bundle is encrypted locally and remains queued until the backend confirms
   successful synchronization.

Submitted visits are immutable. Review decisions and notes are separate audit
events; a surveyor cannot edit a submitted visit.

## 2. Repository layout

| Path | Responsibility |
|---|---|
| `android/app` | Android UI, navigation, authentication state |
| `android/data` | Room database, GNSS trail, API models, offline sync |
| `android/security` | Android Keystore key management |
| `android/core` | Shared Android utilities and theme |
| `backend/app` | Flask API, authentication, validation, geospatial checks, audit |
| `backend/alembic` | Database migrations |
| `react_admin` | React/TypeScript desktop admin dashboard |
| `ofas_admin` | Legacy Flutter dashboard retained during migration |
| `docker-compose.yml` | Local PostgreSQL/PostGIS, object storage, and backend |

## 3. Evidence and trust model

The client is treated as untrusted. The backend must re-check:

- JWT role and surveyor identity.
- Active phone registration and public-key signature.
- Visit ID uniqueness.
- Assignment ownership for the visit date.
- GNSS coordinates, accuracy, and field radius.
- Identity confirmation status.
- Photo hashes and object-storage references.
- Trail hash chain and signatures.
- Audit-chain integrity.

The Android device stores access and refresh tokens in encrypted preferences.
The phone signing key must remain in Android Keystore and must never be
exported. The local Room database must be encrypted before production rollout;
the current schema and migrations must be tested on real devices before
enabling destructive retention cleanup.

## 4. Offline synchronization contract

The local visit state machine is:

```text
QUEUED -> SYNCING -> SYNCED
             |
             +----> FAILED -> SYNCING
```

Rules:

- Never delete a visit before the server returns a successful response.
- Retry only transient network/server responses.
- Preserve rejected records as `FAILED` for inspection and controlled retry.
- Use the immutable `visit_id` as the idempotency key.
- Do not create a second server visit when a retry receives a duplicate response.
- Synchronize assignments and face templates before field work begins.

The Android `SyncWorker` requires network connectivity and uses the configured
API base URL. A release build must replace the example URL at build time:

```text
-PofasApiBaseUrl=https://api.example.org/
```

The build configuration should be made environment-specific for staging and
production; do not ship the example endpoint.

## 5. Backend deployment

### Required production services

- PostgreSQL with PostGIS.
- S3-compatible object storage with private buckets and lifecycle policies.
- HTTPS reverse proxy/load balancer.
- At least two backend workers for availability.
- Centralized logs and health-check monitoring.

### Required environment values

Copy `backend/.env.example` to a secret-managed environment. At minimum set:

- `FLASK_ENV=production`
- Strong random `SECRET_KEY` and `JWT_SECRET_KEY`, each at least 32 bytes.
- Production `DATABASE_URL`.
- Private S3 endpoint, access key, secret, bucket, and region.
- `PASSKEY_RP_ID` and `PASSKEY_ORIGIN` for the deployed admin domain.
- Exact `CORS_ORIGINS` for the admin application.
- A strong initial super-admin password, rotated after first login.

Do not use the development database password, local object-storage credentials,
or default JWT secrets in production.

### Startup sequence

1. Apply Alembic migrations.
2. Verify database readiness.
3. Initialize or rotate the first super-admin credentials through a protected
   operational procedure.
4. Start Gunicorn behind HTTPS.
5. Verify `/health/live` and `/health/ready`.
6. Confirm object-storage upload and download permissions.
7. Register a test phone and complete a staging visit before production use.

## 6. Android release checklist

- Configure the production API URL.
- Use a release signing key; never use the debug signing configuration.
- Confirm the simple identity-confirmation flow is enabled.
- Confirm camera capture is real CameraX capture, not a placeholder preview.
- Confirm runtime permissions for camera, fine location, notifications, and
  background/foreground location behavior on the target Android version.
- Test airplane mode, process death, reboot, battery loss, low storage, poor
  GNSS accuracy, duplicate retry, and clock changes.
- Verify blocked/mock-location devices are rejected.
- Verify the device can recover from a cancelled verification without losing
  queued visits.
- Run the release APK on the exact hardware selected for the pilot.

## 7. Admin operations

Admins should create records in this order:

1. Create the surveyor profile and enroll the face template.
2. Create and validate the field center, radius, crop metadata, and reference
   photos.
3. Register the company phone and verify its public key.
4. Create date-based surveyor/field assignments.
5. Confirm the surveyor downloads assignments while online.
6. Review visits by evidence status and investigate flagged records.

Never change a field coordinate or radius to make an invalid historical visit
pass. Create a new field revision or record an administrative correction in the
audit log.

## 8. Monitoring and incident response

Monitor:

- Backend readiness failures.
- Sync rejection and retry rates.
- Failed visits by phone, surveyor, and field.
- GNSS accuracy and trail gaps.
- Blocked phones and repeated face-verification failures.
- Object-storage failures and database latency.
- Audit-chain verification failures.

If a phone is lost, block it immediately in the admin dashboard. The backend
must reject future submissions from that phone. Preserve its already-uploaded
evidence and investigate any unsynchronized local data through the controlled
device-recovery process.

## 9. Current release gate

The repository now contains production-oriented authentication/session handling,
assignment-backed field loading, GNSS provider integration, offline queue state
transitions, backend identity/assignment checks, and this operational guide.

CameraX photo capture is now implemented and stores local JPEG files with
SHA-256 fingerprints. Room is configured with a device-generated SQLCipher
passphrase protected by encrypted preferences. Existing plaintext installations
must go through a controlled migration or reinstall procedure; never silently
destroy an existing evidence database.

The review screen intentionally refuses submission until the complete visit
bundle is assembled. Identity confirmation is currently a simple explicit
device/field verification action; camera liveness and blink challenges are not
part of the app workflow. It must not be replaced with local placeholders for
location, trail, or photo-upload metadata.

The build must not be called production-ready until these remaining gates are
verified on hardware and in staging:

- Uploading photo bytes to private object storage.
- End-to-end signed visit and trail submission.
- Android device integrity checks.
- Release signing and production API configuration.
- Hardware pilot with offline and recovery scenarios.
