import { FormEvent, ReactNode, useEffect, useState } from "react";
import { api, Assignment, currentSession, Field, ManagedUser, Metrics, Surveyor, Visit, VisitDetail, login, logout } from "./api";

type Section = "overview" | "users" | "visits" | "surveyors" | "fields" | "assignments";

export function App() {
  const [session, setSession] = useState(currentSession());
  if (!session) return <Login onLoggedIn={() => setSession(currentSession())} />;
  return <Dashboard username={session.user.username} role={session.user.role} onLogout={() => { logout(); setSession(null); }} />;
}

function Login({ onLoggedIn }: { onLoggedIn: () => void }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(username, password);
      onLoggedIn();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="login-shell">
    <form className="login-card" onSubmit={submit}>
      <img className="brand-logo login-logo" src="/as-logo.jpg" alt="Army Welfare Trust logo" />
      <p className="eyebrow">FIELD ACTIVITY VERIFICATION</p>
      <h1>OFAS Admin</h1>
      <p className="muted">Review evidence and manage field operations.</p>
      <label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label>
      <label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" /></label>
      {error && <div className="error">{error}</div>}
      <button className="primary wide" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
    </form>
  </main>;
}

function Dashboard({ username, role, onLogout }: { username: string; role: string; onLogout: () => void }) {
  const [section, setSection] = useState<Section>("overview");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [surveyors, setSurveyors] = useState<Surveyor[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.allSettled([api.metrics(), api.users(), api.visits({ per_page: 100 }), api.surveyors(), api.fields(), api.assignments()])
      .then(([metricsResult, usersResult, visitsResult, surveyorsResult, fieldsResult, assignmentsResult]) => {
        const failures: string[] = [];
        if (metricsResult.status === "fulfilled") setMetrics(metricsResult.value);
        else failures.push("metrics");
        if (usersResult.status === "fulfilled") setUsers(usersResult.value.users);
        else failures.push("users");
        if (visitsResult.status === "fulfilled") setVisits(visitsResult.value.visits);
        else failures.push("visits");
        if (surveyorsResult.status === "fulfilled") setSurveyors(surveyorsResult.value.surveyors);
        else failures.push("surveyors");
        if (fieldsResult.status === "fulfilled") setFields(fieldsResult.value.fields);
        else failures.push("fields");
        if (assignmentsResult.status === "fulfilled") setAssignments(assignmentsResult.value.assignments);
        else failures.push("assignments");
        if (failures.length > 0) setError(`Some dashboard data could not be loaded: ${failures.join(", ")}.`);
      });
  }, []);

  const nav = (next: Section) => setSection(next);
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="sidebar-brand"><img className="brand-logo sidebar-logo" src="/as-logo.jpg" alt="Army Welfare Trust logo" /><span>OFAS</span></div>
      <p className="eyebrow sidebar-label">ADMIN CONSOLE</p>
      <nav>
        {(["overview", "users", "visits", "surveyors", "fields", "assignments"] as Section[]).map((item) =>
          <button key={item} className={section === item ? "nav-item active" : "nav-item"} onClick={() => nav(item)}>
            <span>{item === "overview" ? "▦" : item === "users" ? "♙" : item === "visits" ? "◷" : item === "surveyors" ? "♟" : item === "fields" ? "⌖" : "⇄"}</span>
            {item === "visits" ? "Visit Details" : item[0].toUpperCase() + item.slice(1)}
          </button>
        )}
      </nav>
      <div className="sidebar-footer"><span className="status-dot" /> Backend connected</div>
    </aside>
    <main className="content">
      <header className="topbar"><div><p className="eyebrow">CONTROL CENTER</p><h2>{section === "visits" ? "Visit Details" : section[0].toUpperCase() + section.slice(1)}</h2></div><div className="user-menu"><span>{username}</span><small>{role.replace("_", " ")}</small><button onClick={onLogout}>Sign out</button></div></header>
      {error && <div className="error banner">{error}</div>}
      {section === "overview" && <Overview metrics={metrics} visits={visits} onNavigate={nav} />}
      {section === "users" && <Users users={users} surveyors={surveyors} canCreateAdmin={role === "super_admin"} onSurveyorCreated={(surveyor) => setSurveyors((current) => [surveyor, ...current])} onAdminCreated={(user) => setUsers((current) => [user, ...current])} onUsersChanged={setUsers} onSurveyorsChanged={setSurveyors} />}
      {section === "visits" && <VisitDetails visits={visits} surveyors={surveyors} />}
      {section === "surveyors" && <Surveyors surveyors={surveyors} onChanged={(next) => setSurveyors(next)} />}
      {section === "fields" && <Fields fields={fields} assignments={assignments} onFieldCreated={(field) => setFields((current) => [field, ...current])} onChanged={(next) => setFields(next)} />}
      {section === "assignments" && <Assignments assignments={assignments} surveyors={surveyors} fields={fields} onAssignmentCreated={(assignment) => setAssignments((current) => [assignment, ...current])} onChanged={(next) => setAssignments(next)} />}
    </main>
  </div>;
}

function Assignments({ assignments, surveyors, fields, onAssignmentCreated, onChanged }: { assignments: Assignment[]; surveyors: Surveyor[]; fields: Field[]; onAssignmentCreated: (assignment: Assignment) => void; onChanged: (assignments: Assignment[]) => void }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ surveyor_id: "", field_id: "", start_date: "", end_date: "" });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (!form.surveyor_id || !form.field_id || !form.start_date || !form.end_date) {
        setError("Select a surveyor, field, start date, and end date.");
        return;
      }

      if (form.end_date < form.start_date) {
        setError("End date must be on or after the start date.");
        return;
      }
      const response = await api.createAssignment(form);
      const surveyor = surveyors.find((item) => item.id === form.surveyor_id);
      const field = fields.find((item) => item.id === form.field_id);
      onAssignmentCreated({
        id: response.id,
        surveyor_id: form.surveyor_id,
        surveyor_name: surveyor?.full_name ?? null,
        field_id: form.field_id,
        field_code: field?.field_code ?? null,
        start_date: form.start_date,
        end_date: form.end_date,
        is_completed: false,
        completed_at: null
      });
      setForm({ surveyor_id: "", field_id: "", start_date: "", end_date: "" });
      setOpen(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to create assignment.");
    } finally {
      setBusy(false);
    }
  }

  return <div className="page">
    <section className="panel">
      <div className="panel-heading">
        <div><p className="eyebrow">FIELD OPERATIONS</p><h3>Assignments</h3><p className="muted">Assign fields to surveyors and track assignment completion.</p></div>
        <button className="primary" onClick={() => { setOpen(!open); setError(""); }}>{open ? "Cancel" : "Assign field"}</button>
      </div>
      {open && <form className="create-form" onSubmit={submit}>
        <div className="form-grid">
          <label>Surveyor<select required value={form.surveyor_id} onChange={(event) => setForm({ ...form, surveyor_id: event.target.value })}><option value="">Select surveyor</option>{surveyors.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.employee_id} — {item.full_name}</option>)}</select></label>
          <label>Field<select required value={form.field_id} onChange={(event) => setForm({ ...form, field_id: event.target.value })}><option value="">Select field</option>{fields.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.field_code} — {item.name}</option>)}</select></label>
          <label>Start date<input required type="date" value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} /></label>
          <label>End date<input required type="date" min={form.start_date || undefined} value={form.end_date} onChange={(event) => setForm({ ...form, end_date: event.target.value })} /></label>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? "Assigning..." : "Create assignment"}</button>
      </form>}
      <DataTable title="" headers={["Surveyor", "Field", "Start date", "End date", "Status", "Actions"]} rows={assignments.map((assignment) => [
        assignment.surveyor_name ?? assignment.surveyor_id,
        assignment.field_code ?? assignment.field_id,
        assignment.start_date,
        assignment.end_date,
        assignment.is_completed ? "Completed" : "Pending",
        <Actions key={assignment.id}
          onEdit={async () => {
            const start = window.prompt("Start date (YYYY-MM-DD)", assignment.start_date);
            const end = window.prompt("End date (YYYY-MM-DD)", assignment.end_date);
            if (!start || !end) return;
            try { await api.updateAssignment(assignment.id, { start_date: start, end_date: end }); onChanged(assignments.map((item) => item.id === assignment.id ? { ...item, start_date: start, end_date: end } : item)); } catch (cause) { window.alert(cause instanceof Error ? cause.message : "Unable to update assignment."); }
          }}
          onDelete={async () => {
            if (!window.confirm("Delete this assignment?")) return;
            try { await api.deleteAssignment(assignment.id); onChanged(assignments.filter((item) => item.id !== assignment.id)); } catch (cause) { window.alert(cause instanceof Error ? cause.message : "Unable to delete assignment."); }
          }} />
      ])} />
    </section>
  </div>;
}

function VisitDetails({ visits, surveyors }: { visits: Visit[]; surveyors: Surveyor[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [surveyorId, setSurveyorId] = useState("");
  const [filteredVisits, setFilteredVisits] = useState(visits);
  const [detail, setDetail] = useState<VisitDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const next = visits.filter((visit) =>
      (!status || visit.review_status === status || visit.status === status) &&
      (!surveyorId || visit.surveyor_id === surveyorId)
    );
    setFilteredVisits(next);
    if (selectedId && !next.some((visit) => visit.id === selectedId)) {
      setSelectedId(null);
      setDetail(null);
    }
  }, [visits, status, surveyorId, selectedId]);

  async function selectVisit(id: string) {
    setSelectedId(id);
    setLoading(true);
    setError("");
    try {
      setDetail(await api.visitDetail(id));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load visit details.");
    } finally {
      setLoading(false);
    }
  }

  return <div className="page">
    <section className="panel">
      <div className="panel-heading">
        <div><p className="eyebrow">AUDIT TRAIL</p><h3>Visit details</h3><p className="muted">Review field visits submitted by surveyors.</p></div>
      </div>
      <div className="filter-bar">
        <label>Surveyor<select value={surveyorId} onChange={(event) => setSurveyorId(event.target.value)}><option value="">All surveyors</option>{surveyors.map((surveyor) => <option key={surveyor.id} value={surveyor.id}>{surveyor.employee_id} — {surveyor.full_name}</option>)}</select></label>
        <label>Status<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{["queued", "syncing", "synced", "failed", "valid", "invalid", "flagged"].map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
      </div>
      {error && <div className="error">{error}</div>}
      <DataTable title="" headers={["Visit", "Surveyor", "Field", "Captured", "GPS", "Status", "Review"]} rows={filteredVisits.map((visit) => [
        <button type="button" className="link-button" onClick={() => void selectVisit(visit.id)}>{visit.visit_id}</button>,
        visit.surveyor_name ?? "—",
        visit.field_code ?? "—",
        new Date(visit.satellite_timestamp).toLocaleString(),
        `${visit.latitude.toFixed(5)}, ${visit.longitude.toFixed(5)}`,
        visit.status,
        visit.review_status ?? "Unreviewed"
      ])} />
    </section>
    {selectedId && <section className="panel detail-panel">
      <div className="panel-heading"><div><p className="eyebrow">SELECTED VISIT</p><h3>{detail?.visit.visit_id ?? selectedId}</h3></div>{loading && <span className="muted">Loading...</span>}</div>
      {detail && <div className="detail-grid">
        <DetailItem label="Surveyor" value={detail.visit.surveyor ? `${detail.visit.surveyor.employee_id} — ${detail.visit.surveyor.full_name}` : "—"} />
        <DetailItem label="Field" value={detail.visit.field ? `${detail.visit.field.field_code} — ${detail.visit.field.name}` : "—"} />
        <DetailItem label="Captured" value={new Date(detail.visit.satellite_timestamp).toLocaleString()} />
        <DetailItem label="Coordinates" value={`${detail.visit.latitude}, ${detail.visit.longitude}`} />
        <DetailItem label="GPS accuracy" value={`${detail.visit.accuracy_meters} m`} />
        <DetailItem label="Phone" value={detail.visit.phone_id} />
        <DetailItem label="Visit status" value={detail.visit.status} />
        <DetailItem label="Review" value={detail.visit.review_status ?? "Unreviewed"} />
        <DetailItem label="Face match" value={detail.visit.face_match_score == null ? "—" : `${(detail.visit.face_match_score * 100).toFixed(1)}%`} />
        <DetailItem label="Liveness" value={detail.visit.liveness_verified ? "Verified" : "Not verified"} />
        <DetailItem label="Trail points" value={String(detail.trail_entries.length)} />
        <DetailItem label="Review notes" value={detail.visit.review_notes ?? "—"} />
      </div>}
    </section>}
  </div>;
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return <div className="detail-item"><span>{label}</span><strong>{value}</strong></div>;
}

function Fields({ fields, assignments, onFieldCreated, onChanged }: { fields: Field[]; assignments: Assignment[]; onFieldCreated: (field: Field) => void; onChanged: (fields: Field[]) => void }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ field_code: "", name: "", crop_type: "", center_lat: "", center_lon: "", radius_meters: "100" });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const fieldCode = form.field_code.toUpperCase();
      if (!/^[A-Z0-9_-]{3,50}$/.test(fieldCode)) {
        setError("Field code must be 3-50 uppercase letters, numbers, underscores, or hyphens.");
        return;
      }
      const centerLat = Number(form.center_lat);
      const centerLon = Number(form.center_lon);
      const radiusMeters = Number(form.radius_meters);
      if (!Number.isFinite(centerLat) || centerLat < -90 || centerLat > 90 ||
          !Number.isFinite(centerLon) || centerLon < -180 || centerLon > 180) {
        setError("Latitude must be between -90 and 90 and longitude between -180 and 180.");
        return;
      }
      if (!Number.isFinite(radiusMeters) || radiusMeters <= 0) {
        setError("Radius must be greater than zero.");
        return;
      }
      const response = await api.createField({
        field_code: fieldCode,
        name: form.name,
        crop_type: form.crop_type || undefined,
        center_lat: centerLat,
        center_lon: centerLon,
        radius_meters: radiusMeters
      });
      onFieldCreated({
        id: response.id, field_code: fieldCode, name: form.name, crop_type: form.crop_type || null,
        center_lat: centerLat, center_lon: centerLon, radius_meters: radiusMeters,
        is_active: true, created_at: new Date().toISOString()
      });
      setForm({ field_code: "", name: "", crop_type: "", center_lat: "", center_lon: "", radius_meters: "100" });
      setOpen(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to create field.");
    } finally {
      setBusy(false);
    }
  }

  return <div className="page">
    <section className="panel">
      <div className="panel-heading">
        <div><p className="eyebrow">FIELD MANAGEMENT</p><h3>Fields</h3><p className="muted">Manage field locations used for surveyor assignments.</p></div>
        <button className="primary" onClick={() => { setOpen(!open); setError(""); }}>{open ? "Cancel" : "Add field"}</button>
      </div>
      {open && <form className="create-form" onSubmit={submit}>
        <div className="form-grid">
          <label>Field code<input required minLength={3} maxLength={50} placeholder="FIELD-001" value={form.field_code} onChange={(event) => setForm({ ...form, field_code: event.target.value.toUpperCase() })} /></label>
          <label>Name<input required maxLength={200} placeholder="North farm" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
          <label>Crop type<input maxLength={100} placeholder="Wheat" value={form.crop_type} onChange={(event) => setForm({ ...form, crop_type: event.target.value })} /></label>
          <label>Latitude<input required type="number" min="-90" max="90" step="any" placeholder="28.6139" value={form.center_lat} onChange={(event) => setForm({ ...form, center_lat: event.target.value })} /></label>
          <label>Longitude<input required type="number" min="-180" max="180" step="any" placeholder="77.2090" value={form.center_lon} onChange={(event) => setForm({ ...form, center_lon: event.target.value })} /></label>
          <label>Radius (meters)<input required type="number" min="1" step="any" value={form.radius_meters} onChange={(event) => setForm({ ...form, radius_meters: event.target.value })} /></label>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? "Creating..." : "Create field"}</button>
      </form>}
      <DataTable title="" headers={["Code", "Name", "Crop", "Latitude", "Longitude", "Radius", "Status", "Actions"]} rows={fields.map((field) => [
        field.field_code, field.name, field.crop_type ?? "—", field.center_lat.toFixed(6), field.center_lon.toFixed(6),
        `${field.radius_meters} m`, assignments.some((assignment) => assignment.field_id === field.id) ? "Assigned" : "Unassigned",
        <Actions key={field.id}
          onEdit={async () => {
            const name = window.prompt("Field name", field.name);
            if (!name) return;
            try { await api.updateField(field.id, { name, crop_type: field.crop_type ?? "", center_lat: field.center_lat, center_lon: field.center_lon, radius_meters: field.radius_meters }); onChanged(fields.map((item) => item.id === field.id ? { ...item, name } : item)); } catch (cause) { window.alert(cause instanceof Error ? cause.message : "Unable to update field."); }
          }}
          onDelete={async () => {
            if (!window.confirm("Deactivate this field? Historical visits will remain available.")) return;
            try { await api.deleteField(field.id); onChanged(fields.map((item) => item.id === field.id ? { ...item, is_active: false } : item)); } catch (cause) { window.alert(cause instanceof Error ? cause.message : "Unable to deactivate field."); }
          }} />
      ])} />
    </section>
  </div>;
}

function Surveyors({ surveyors, onChanged }: { surveyors: Surveyor[]; onChanged: (surveyors: Surveyor[]) => void }) {
  const [editing, setEditing] = useState<Surveyor | null>(null);
  const [form, setForm] = useState({ full_name: "", phone_number: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function beginEdit(surveyor: Surveyor) {
    setEditing(surveyor);
    setForm({ full_name: surveyor.full_name, phone_number: surveyor.phone_number ?? "", password: "" });
    setError("");
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!editing) return;
    if (!form.full_name.trim() || !/^\+?[1-9]\d{1,14}$/.test(form.phone_number)) {
      setError("Enter a name and a valid phone number.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.updateSurveyor(editing.id, {
        full_name: form.full_name.trim(),
        phone_number: form.phone_number,
        ...(form.password ? { password: form.password } : {})
      });
      onChanged(surveyors.map((item) => item.id === editing.id
        ? { ...item, full_name: form.full_name.trim(), phone_number: form.phone_number }
        : item));
      setEditing(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update surveyor.");
    } finally {
      setBusy(false);
    }
  }

  async function toggle(surveyor: Surveyor) {
    const action = surveyor.is_active ? "deactivate" : "activate";
    if (!window.confirm(`Are you sure you want to ${action} ${surveyor.full_name}?`)) return;
    try {
      await api.updateSurveyor(surveyor.id, { is_active: !surveyor.is_active });
      onChanged(surveyors.map((item) => item.id === surveyor.id ? { ...item, is_active: !surveyor.is_active } : item));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `Unable to ${action} surveyor.`);
    }
  }

  return <div className="page"><section className="panel"><div className="panel-heading"><div><p className="eyebrow">FIELD OPERATIONS</p><h3>Surveyors</h3><p className="muted">Edit or activate/deactivate surveyor accounts.</p></div></div>
    {editing && <form className="create-form edit-form" onSubmit={save}>
      <div className="form-heading"><div><h3>Edit surveyor</h3><p className="muted">Update profile details or set a new password.</p></div><button type="button" className="link-button" onClick={() => setEditing(null)}>Cancel</button></div>
      <div className="form-grid">
        <label>Full name<input required maxLength={200} value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label>
        <label>Phone number<input required type="tel" value={form.phone_number} onChange={(event) => setForm({ ...form, phone_number: event.target.value })} /></label>
        <label>New password<input minLength={12} type="password" placeholder="Leave blank to keep current password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
      </div>
      {error && <div className="error">{error}</div>}
      <button className="primary" disabled={busy}>{busy ? "Saving..." : "Save surveyor"}</button>
    </form>}
    <DataTable title="" headers={["Employee ID", "Name", "Phone", "Email", "Status", "Actions"]} rows={surveyors.map((surveyor) => [
      surveyor.employee_id, surveyor.full_name, surveyor.phone_number ?? "—", surveyor.email ?? "—", surveyor.is_active ? "Active" : "Inactive",
      <Actions key={surveyor.id} onEdit={() => beginEdit(surveyor)} onToggle={() => toggle(surveyor)} active={surveyor.is_active} />
    ])} />
  </section></div>;
}

function Actions({ onEdit, onDelete, onToggle, active = true }: { onEdit: () => void; onDelete?: () => void; onToggle?: () => void; active?: boolean }) {
  return <div className="row-actions">
    <button type="button" className="link-button" onClick={onEdit}>Edit</button>
    {onToggle && <button type="button" className="link-button danger" onClick={onToggle}>{active ? "Deactivate" : "Activate"}</button>}
    {onDelete && <button type="button" className="link-button danger" onClick={onDelete}>Delete</button>}
  </div>;
}

function Users({ users, surveyors, canCreateAdmin, onSurveyorCreated, onAdminCreated, onUsersChanged, onSurveyorsChanged }: { users: ManagedUser[]; surveyors: Surveyor[]; canCreateAdmin: boolean; onSurveyorCreated: (surveyor: Surveyor) => void; onAdminCreated: (user: ManagedUser) => void; onUsersChanged: (users: ManagedUser[]) => void; onSurveyorsChanged: (surveyors: Surveyor[]) => void }) {
  const [formType, setFormType] = useState<"admin" | "surveyor" | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [adminForm, setAdminForm] = useState({ username: "", email: "", password: "" });
  const [surveyorForm, setSurveyorForm] = useState({ employee_id: "", full_name: "", phone_number: "", password: "" });
  const [editing, setEditing] = useState<{ type: "admin" | "surveyor"; id: string } | null>(null);
  const [editError, setEditError] = useState("");
  const [editBusy, setEditBusy] = useState(false);
  const [adminEdit, setAdminEdit] = useState({ email: "", password: "" });
  const [surveyorEdit, setSurveyorEdit] = useState({ full_name: "", phone_number: "", password: "" });

  async function submitForm(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (formType === "admin") {
        if (!/^[A-Za-z0-9_-]+$/.test(adminForm.username)) {
          setError("Username may contain only letters, numbers, underscores, and hyphens.");
          return;
        }

        const response = await api.createAdmin(adminForm);
        onAdminCreated({
          id: response.id, username: adminForm.username, email: adminForm.email, role: "admin",
          totp_enabled: false, is_active: true, created_at: new Date().toISOString(), last_login: null
        });
        setAdminForm({ username: "", email: "", password: "" });
      } else {
        const employeeId = surveyorForm.employee_id.toUpperCase();
        if (!/^[A-Z0-9_-]{3,50}$/.test(employeeId)) {
          setError("Employee ID must be 3-50 uppercase letters, numbers, underscores, or hyphens.");
          return;
        }
        const response = await api.createSurveyor({ ...surveyorForm, employee_id: employeeId });
        onSurveyorCreated({
          id: response.id, employee_id: employeeId, full_name: surveyorForm.full_name,
          phone_number: surveyorForm.phone_number, email: null,
          is_active: true, created_at: new Date().toISOString()
        });
        setSurveyorForm({ employee_id: "", full_name: "", phone_number: "", password: "" });
      }
      setFormType(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `Unable to create ${formType ?? "account"}.`);
    } finally {
      setBusy(false);
    }
  }

  function beginAdminEdit(user: ManagedUser) {
    setEditing({ type: "admin", id: user.id });
    setAdminEdit({ email: user.email, password: "" });
    setEditError("");
  }

  function beginSurveyorEdit(surveyor: Surveyor) {
    setEditing({ type: "surveyor", id: surveyor.id });
    setSurveyorEdit({ full_name: surveyor.full_name, phone_number: surveyor.phone_number ?? "", password: "" });
    setEditError("");
  }

  async function saveEdit(event: FormEvent) {
    event.preventDefault();
    if (!editing) return;
    setEditError("");
    setEditBusy(true);
    try {
      if (editing.type === "admin") {
        if (!adminEdit.email || !adminEdit.email.includes("@")) {
          setEditError("Enter a valid administrator email.");
          return;
        }
        const payload = { email: adminEdit.email, ...(adminEdit.password ? { password: adminEdit.password } : {}) };
        await api.updateUser(editing.id, payload);
        onUsersChanged(users.map((user) => user.id === editing.id ? { ...user, email: adminEdit.email } : user));
      } else {
        if (!surveyorEdit.full_name.trim() || !/^\+?[1-9]\d{1,14}$/.test(surveyorEdit.phone_number)) {
          setEditError("Enter a name and a valid phone number.");
          return;
        }
        const payload = {
          full_name: surveyorEdit.full_name.trim(),
          phone_number: surveyorEdit.phone_number,
          ...(surveyorEdit.password ? { password: surveyorEdit.password } : {})
        };
        await api.updateSurveyor(editing.id, payload);
        onSurveyorsChanged(surveyors.map((surveyor) => surveyor.id === editing.id
          ? { ...surveyor, full_name: payload.full_name, phone_number: payload.phone_number }
          : surveyor));
      }
      setEditing(null);
    } catch (cause) {
      setEditError(cause instanceof Error ? cause.message : "Unable to save changes.");
    } finally {
      setEditBusy(false);
    }
  }

  async function toggleAdmin(user: ManagedUser) {
    const action = user.is_active ? "deactivate" : "activate";
    if (!window.confirm(`Are you sure you want to ${action} ${user.username}?`)) return;
    try {
      await api.updateUser(user.id, { is_active: !user.is_active });
      onUsersChanged(users.map((item) => item.id === user.id ? { ...item, is_active: !user.is_active } : item));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `Unable to ${action} administrator.`);
    }
  }

  async function toggleSurveyor(surveyor: Surveyor) {
    const action = surveyor.is_active ? "deactivate" : "activate";
    if (!window.confirm(`Are you sure you want to ${action} ${surveyor.full_name}?`)) return;
    try {
      await api.updateSurveyor(surveyor.id, { is_active: !surveyor.is_active });
      onSurveyorsChanged(surveyors.map((item) => item.id === surveyor.id ? { ...item, is_active: !surveyor.is_active } : item));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `Unable to ${action} surveyor.`);
    }
  }

  return <div className="page">
    <section className="panel">
      <div className="panel-heading">
        <div><p className="eyebrow">ACCESS CONTROL</p><h3>System users</h3><p className="muted">All administrators, super administrators, and surveyor accounts.</p></div>
        <div className="action-group">
          <button className="primary" onClick={() => setFormType(formType === "surveyor" ? null : "surveyor")}>{formType === "surveyor" ? "Cancel" : "Create surveyor"}</button>
          {canCreateAdmin && <button className="secondary" onClick={() => setFormType(formType === "admin" ? null : "admin")}>{formType === "admin" ? "Cancel" : "Create admin"}</button>}
        </div>
      </div>
      {!canCreateAdmin && <div className="notice">Regular admins can create and manage surveyor accounts. Only a super admin can create administrator accounts.</div>}
      {formType === "admin" && <form className="create-form" onSubmit={submitForm}>
        <div className="form-heading"><div><h3>Create administrator</h3><p className="muted">The new account will be created with the <strong>admin</strong> role.</p></div></div>
        <div className="form-grid">
          <label>Username<input required minLength={3} maxLength={50} value={adminForm.username} onChange={(event) => setAdminForm({ ...adminForm, username: event.target.value })} /></label>
          <label>Email<input required type="email" value={adminForm.email} onChange={(event) => setAdminForm({ ...adminForm, email: event.target.value })} /></label>
          <label>Password<input required minLength={12} type="password" placeholder="12+ characters" value={adminForm.password} onChange={(event) => setAdminForm({ ...adminForm, password: event.target.value })} /></label>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? "Creating..." : "Create administrator"}</button>
      </form>}
      {formType === "surveyor" && <form className="create-form" onSubmit={submitForm}>
        <div className="form-heading"><div><h3>Create surveyor</h3><p className="muted">Create the surveyor profile used for assignments and field visits.</p></div></div>
        <div className="form-grid">
          <label>Employee ID<input required minLength={3} maxLength={50} placeholder="SURV-001" value={surveyorForm.employee_id} onChange={(event) => setSurveyorForm({ ...surveyorForm, employee_id: event.target.value.toUpperCase() })} /></label>
          <label>Full name<input required maxLength={200} value={surveyorForm.full_name} onChange={(event) => setSurveyorForm({ ...surveyorForm, full_name: event.target.value })} /></label>
          <label>Phone number<input required type="tel" placeholder="+1234567890" value={surveyorForm.phone_number} onChange={(event) => setSurveyorForm({ ...surveyorForm, phone_number: event.target.value })} /></label>
          <label>Password<input required minLength={12} type="password" placeholder="12+ characters" value={surveyorForm.password} onChange={(event) => setSurveyorForm({ ...surveyorForm, password: event.target.value })} /></label>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={busy}>{busy ? "Creating..." : "Create surveyor"}</button>
      </form>}
      {editing?.type === "admin" && <form className="create-form edit-form" onSubmit={saveEdit}>
        <div className="form-heading"><div><h3>Edit administrator</h3><p className="muted">Update the email or leave the password blank to keep it unchanged.</p></div><button type="button" className="link-button" onClick={() => setEditing(null)}>Cancel</button></div>
        <div className="form-grid">
          <label>Email<input required type="email" value={adminEdit.email} onChange={(event) => setAdminEdit({ ...adminEdit, email: event.target.value })} /></label>
          <label>New password<input minLength={12} type="password" placeholder="Leave blank to keep current password" value={adminEdit.password} onChange={(event) => setAdminEdit({ ...adminEdit, password: event.target.value })} /></label>
        </div>
        {editError && <div className="error">{editError}</div>}
        <button className="primary" disabled={editBusy}>{editBusy ? "Saving..." : "Save administrator"}</button>
      </form>}
      {editing?.type === "surveyor" && <form className="create-form edit-form" onSubmit={saveEdit}>
        <div className="form-heading"><div><h3>Edit surveyor</h3><p className="muted">Update profile details or set a new password.</p></div><button type="button" className="link-button" onClick={() => setEditing(null)}>Cancel</button></div>
        <div className="form-grid">
          <label>Full name<input required maxLength={200} value={surveyorEdit.full_name} onChange={(event) => setSurveyorEdit({ ...surveyorEdit, full_name: event.target.value })} /></label>
          <label>Phone number<input required type="tel" value={surveyorEdit.phone_number} onChange={(event) => setSurveyorEdit({ ...surveyorEdit, phone_number: event.target.value })} /></label>
          <label>New password<input minLength={12} type="password" placeholder="Leave blank to keep current password" value={surveyorEdit.password} onChange={(event) => setSurveyorEdit({ ...surveyorEdit, password: event.target.value })} /></label>
        </div>
        {editError && <div className="error">{editError}</div>}
        <button className="primary" disabled={editBusy}>{editBusy ? "Saving..." : "Save surveyor"}</button>
      </form>}
      <DataTable title="" headers={["Username", "Email", "Role", "MFA", "Created", "Last login", "Status", "Actions"]} rows={users.map((user) => [
        user.username,
        user.email,
        user.role.replace("_", " "),
        user.totp_enabled ? "Enabled" : "Not enabled",
        new Date(user.created_at).toLocaleDateString(),
        user.last_login ? new Date(user.last_login).toLocaleString() : "Never",
        user.is_active ? "Active" : "Inactive",
        canCreateAdmin
          ? <Actions key={user.id} onEdit={() => beginAdminEdit(user)} onToggle={() => toggleAdmin(user)} active={user.is_active} />
          : "—"
      ])} />
      <div className="subtable-heading"><h3>Surveyor accounts</h3><span className="muted">{surveyors.length} shown</span></div>
      <DataTable title="" headers={["Employee ID", "Name", "Phone", "Email", "Created", "Status", "Actions"]} rows={surveyors.map((surveyor) => [
        surveyor.employee_id, surveyor.full_name, surveyor.phone_number ?? "—", surveyor.email ?? "—",
        new Date(surveyor.created_at).toLocaleDateString(), surveyor.is_active ? "Active" : "Inactive",
        <Actions key={surveyor.id} onEdit={() => beginSurveyorEdit(surveyor)} onToggle={() => toggleSurveyor(surveyor)} active={surveyor.is_active} />
      ])} />
    </section>
  </div>;
}

function Overview({ metrics, visits, onNavigate }: { metrics: Metrics | null; visits: Visit[]; onNavigate: (section: Section) => void }) {
  const counts = metrics?.counts;
  return <div className="page">
    <div className="stat-grid">
      <Stat label="Total visits" value={counts?.visits ?? "—"} accent="green" />
      <Stat label="Active surveyors" value={counts?.surveyors ?? "—"} accent="blue" />
      <Stat label="Registered fields" value={counts?.fields ?? "—"} accent="gold" />
      <Stat label="Registered phones" value={counts?.phones ?? "—"} accent="purple" />
    </div>
    <section className="panel"><div className="panel-heading"><div><p className="eyebrow">AUDIT QUEUE</p><h3>Recent field visits</h3></div><button className="link-button" onClick={() => onNavigate("visits")}>View all →</button></div>
      <DataTable compact title="" headers={["Visit", "Surveyor", "Field", "Captured", "Review"]} rows={visits.slice(0, 5).map((visit) => [visit.visit_id, visit.surveyor_name ?? "—", visit.field_code ?? "—", new Date(visit.satellite_timestamp).toLocaleDateString(), visit.review_status ?? "pending"])} />
    </section>
  </div>;
}

function Stat({ label, value, accent }: { label: string; value: string | number; accent: string }) {
  return <div className={`stat-card ${accent}`}><span className="stat-icon">◆</span><p>{label}</p><strong>{value}</strong><small>Live from backend</small></div>;
}

function DataTable({ title, headers, rows, compact = false }: { title: string; headers: string[]; rows: Array<Array<ReactNode>>; compact?: boolean }) {
  return <section className={compact ? "table-wrap compact" : "panel table-wrap"}>{title && <div className="panel-heading"><h3>{title}</h3><span className="muted">{rows.length} shown</span></div>}<div className="table-scroll"><table><thead><tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, index) => <tr key={index}>{row.map((cell, cellIndex) => <td key={cellIndex}>{cellIndex === row.length - 1 ? cell : cell}</td>)}</tr>) : <tr><td colSpan={headers.length} className="empty">No records found.</td></tr>}</tbody></table></div></section>;
}
