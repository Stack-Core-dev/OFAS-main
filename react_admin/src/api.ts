export type Role = "admin" | "super_admin" | "surveyor";

export type User = {
  id: string;
  username: string;
  role: Role;
};

export type AuthSession = {
  access_token: string;
  refresh_token: string;
  user: User;
};

export type Metrics = {
  counts: {
    users: number;
    surveyors: number;
    fields: number;
    visits: number;
    phones: number;
  };
};

export type FieldPhoto = {
  hash: string;
  s3_key: string | null;
  timestamp: string;
  latitude?: number | null;
  longitude?: number | null;
  accuracy_meters?: number | null;
};

export type Visit = {
  id: string;
  visit_id: string;
  surveyor_id: string;
  surveyor_name: string | null;
  field_code: string | null;
  satellite_timestamp: string;
  latitude: number;
  longitude: number;
  review_status: string | null;
  status: string;
  accuracy_meters: number | null;
  altitude?: number | null;
  speed?: number | null;
  bearing?: number | null;
  selfie_photo_s3_key?: string | null;
  selfie_latitude?: number | null;
  selfie_longitude?: number | null;
  selfie_accuracy_meters?: number | null;
  field_photos?: FieldPhoto[] | null;
  face_match_score?: number | null;
  liveness_verified?: boolean;
  synced_at?: string | null;
  reviewed_at?: string | null;
  review_notes?: string | null;
};

export type VisitDetail = {
  visit: Visit & {
    surveyor: { id: string; employee_id: string; full_name: string } | null;
    field: { id: string; field_code: string; name: string; center_lat: number; center_lon: number; radius_meters: number } | null;
    phone_id: string;
    selfie_photo_hash: string;
    selfie_latitude?: number | null;
    selfie_longitude?: number | null;
    selfie_accuracy_meters?: number | null;
    trail_snapshot: unknown;
    signature: string;
    signed_by_key_id: string;
    reviewed_by: string | null;
    reviewed_at: string | null;
  };
  trail_entries: Array<{
    sequence_number: number;
    satellite_timestamp: string;
    latitude: number;
    longitude: number;
    accuracy_meters: number;
    entry_hash: string;
    prev_hash: string | null;
  }>;
};

export type Surveyor = {
  id: string;
  employee_id: string;
  full_name: string;
  phone_number: string | null;
  email: string | null;
  is_active: boolean;
  created_at: string;
  face_registration_status?: "registered" | "not_registered";
  face_template_version?: number;
  face_template_updated_at?: string | null;
};

export type Field = {
  id: string;
  field_code: string;
  name: string;
  crop_type: string | null;
  center_lat: number;
  center_lon: number;
  radius_meters: number;
  is_active: boolean;
  created_at: string;
};

export type ManagedUser = {
  id: string;
  username: string;
  email: string;
  role: Role;
  totp_enabled: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
};

export type Assignment = {
  id: string;
  surveyor_id: string;
  surveyor_name: string | null;
  field_id: string;
  field_code: string | null;
  start_date: string;
  end_date: string;
  is_completed: boolean;
  completed_at: string | null;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

let session: AuthSession | null = loadSession();

function loadSession(): AuthSession | null {
  const raw = localStorage.getItem("ofas_admin_session");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    localStorage.removeItem("ofas_admin_session");
    return null;
  }
}

function saveSession(next: AuthSession | null) {
  session = next;
  if (next) localStorage.setItem("ofas_admin_session", JSON.stringify(next));
  else localStorage.removeItem("ofas_admin_session");
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (session?.access_token) headers.set("Authorization", `Bearer ${session.access_token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (response.status === 401 && retry && session?.refresh_token) {
    const refreshed = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.refresh_token}`, "Content-Type": "application/json" }
    });
    if (refreshed.ok) {
      saveSession(await refreshed.json() as AuthSession);
      return request<T>(path, init, false);
    }
    saveSession(null);
  }

  const body = await response.json().catch(() => ({})) as { error?: string; details?: string[] };
  if (!response.ok) {
    const message = body.details?.length
      ? `${body.error ?? "Validation failed"}: ${body.details.join("; ")}`
      : body.error ?? `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body as T;
}

export function currentSession() {
  return session;
}

export function logout() {
  saveSession(null);
}

export async function photoObjectUrl(s3Key: string): Promise<string> {
  const headers = new Headers();
  if (session?.access_token) headers.set("Authorization", `Bearer ${session.access_token}`);
  const encoded = s3Key.split("/").map(encodeURIComponent).join("/");
  const response = await fetch(`${API_BASE_URL}/api/review/photos/${encoded}/raw`, { headers });
  if (!response.ok) throw new Error(`Photo unavailable (${response.status})`);
  return URL.createObjectURL(await response.blob());
}

export async function login(username: string, password: string, totpToken?: string) {
  const response = await request<AuthSession | { requires_totp: true; challenge: string }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password, ...(totpToken ? { totp_token: totpToken } : {}) })
  }, false);
  if ("requires_totp" in response) throw new Error("This account requires a TOTP code.");
  if (!["admin", "super_admin"].includes(response.user.role)) throw new Error("This account is not an admin.");
  saveSession(response);
  return response;
}

export const api = {
  metrics: () => request<Metrics>("/health/metrics"),
  faceRegistrationStats: () => request<{
    summary: { total_surveyors: number; face_registered: number; face_not_registered: number; registration_rate: number };
    registered: Array<{ id: string; employee_id: string; full_name: string; face_template_version: number; updated_at: string }>;
    not_registered: Array<{ id: string; employee_id: string; full_name: string }>;
  }>("/api/admin/surveyors/face-registration-stats"),
  visits: (params: { per_page?: number; status?: string; surveyor_id?: string } = {}) => {
    const query = new URLSearchParams({ per_page: String(params.per_page ?? 100) });
    if (params.status) query.set("status", params.status);
    if (params.surveyor_id) query.set("surveyor_id", params.surveyor_id);
    return request<{ visits: Visit[]; pagination: { total: number } }>(`/api/review/visits?${query.toString()}`);
  },
  visitDetail: (id: string) => request<VisitDetail>(`/api/review/visits/${id}`),
  reviewVisit: (id: string, decision: "VALID" | "INVALID" | "FLAGGED", notes = "") =>
    request<{ message: string; review_status: string; reviewed_at: string }>(`/api/review/visits/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ decision, notes })
    }),
  surveyors: () => request<{ surveyors: Surveyor[] }>("/api/admin/surveyors?per_page=100&active=false"),
  fields: () => request<{ fields: Field[] }>("/api/admin/fields?per_page=100"),
  assignments: () => request<{ assignments: Assignment[] }>("/api/admin/assignments?per_page=200"),
  users: () => request<{ users: ManagedUser[] }>("/api/admin/users?per_page=100"),
  createSurveyor: (payload: { employee_id: string; full_name: string; phone_number: string; password: string }) =>
    request<{ id: string; message: string }>("/api/admin/surveyors", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  createAdmin: (payload: { username: string; email: string; password: string }) =>
    request<{ id: string; message: string }>("/api/admin/users", {
      method: "POST",
      body: JSON.stringify({ ...payload, role: "admin" })
    }),
  updateUser: (id: string, payload: { email?: string; password?: string; is_active?: boolean }) =>
    request<{ message: string }>(`/api/admin/users/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteUser: (id: string) =>
    request<{ message: string }>(`/api/admin/users/${id}`, { method: "DELETE" }),
  createField: (payload: { field_code: string; name: string; crop_type?: string; center_lat: number; center_lon: number; radius_meters: number }) =>
    request<{ id: string; message: string }>("/api/admin/fields", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  createAssignment: (payload: { surveyor_id: string; field_id: string; start_date: string; end_date: string }) =>
    request<{ id: string; message: string }>("/api/admin/assignments", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  updateSurveyor: (id: string, payload: { full_name?: string; phone_number?: string; password?: string; is_active?: boolean }) =>
    request<{ message: string }>(`/api/admin/surveyors/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteSurveyor: (id: string) =>
    request<{ message: string }>(`/api/admin/surveyors/${id}`, { method: "DELETE" }),
  updateField: (id: string, payload: { name: string; crop_type?: string; center_lat: number; center_lon: number; radius_meters: number }) =>
    request<{ message: string }>(`/api/admin/fields/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteField: (id: string) =>
    request<{ message: string }>(`/api/admin/fields/${id}`, { method: "DELETE" }),
  updateAssignment: (id: string, payload: { start_date: string; end_date: string }) =>
    request<{ message: string }>(`/api/admin/assignments/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteAssignment: (id: string) =>
    request<{ message: string }>(`/api/admin/assignments/${id}`, { method: "DELETE" })
};
