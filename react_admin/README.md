# OFAS React Admin

Desktop web dashboard for OFAS administrators. The Kotlin application remains
the surveyor mobile client; this app is the browser-based admin client.

The **Users** section shows all system users, including their role, email,
MFA status, activity status, creation date, and last login. Only a
`super_admin` can create an administrator account. New administrators are
created through the protected `POST /api/admin/users` API and must satisfy the
backend password policy.

Super administrators can also edit an administrator email address or deactivate
an account from the Users table. Deactivation is a soft operation that preserves
the account and audit history while preventing future login. The authenticated
administrator cannot deactivate their own account.

## Development

```powershell
Set-Location react_admin
npm install
npm run dev
```

Open `http://localhost:5173`. The backend must be running at
`http://localhost:5000`, or set `VITE_API_BASE_URL` in `.env`.

## Production build

```powershell
npm run build
```

The dashboard only permits `admin` and `super_admin` accounts. Authorization is
still enforced by the Flask API; the browser role check is only a user-facing
guard.
