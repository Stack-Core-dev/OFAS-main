# OFAS

OFAS is an offline-first field activity verification system for agricultural
survey teams. It records who visited a farm, where they were, when they were
there, and the supporting photo/trail evidence even when the device has no
mobile coverage.

The repository contains the Android surveyor app, Flask/PostGIS backend, and
React/TypeScript desktop admin dashboard. The previous Flutter dashboard is
retained under `ofas_admin` during the migration and is not the primary admin
client.

## Quick start

```powershell
docker compose up --build
```

The backend is available at `http://localhost:5000` and the React admin
dashboard at `http://localhost:5173`. Android development uses the Gradle
project under `android`; the dashboard source is under `react_admin`.

Run the admin dashboard:

```powershell
Set-Location react_admin
npm install
npm run dev
```

Run validation:

```powershell
Set-Location backend
venv-311\Scripts\python.exe -m pytest -q

Set-Location ..\android
.\gradlew.bat test
```

## Documentation

Read [docs/OFAS_PRODUCTION_GUIDE.md](docs/OFAS_PRODUCTION_GUIDE.md) for the
product workflow, architecture, security model, offline synchronization,
deployment, operations, and release gates. `IMPLEMENTATION_PLAN.md` contains
the original phased delivery plan.

## Important

The project is not safe to deploy solely because the test suite passes. Real
device validation is required for camera/liveness, GNSS behavior, encrypted
local storage, object-storage uploads, signed evidence, and offline recovery.



#   CURENTLY UNDER DEVELOPMENT