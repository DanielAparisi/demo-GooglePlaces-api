import { API_URL } from './config';
import type {
  ApiStatus,
  Canal,
  GeneracionTipo,
  LaunchResult,
  LlamadaEstado,
  ModeloOportunidad,
  RawLead,
} from '../types/lead';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    let detail = res.statusText || 'Error';
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* la respuesta no era JSON */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

export const api = {
  getLeads: () => request<RawLead[]>('/api/leads'),
  getStatus: () => request<ApiStatus>('/api/status'),

  setSelection: (ids: number[], selected: boolean) =>
    request('/api/leads/select', json('PATCH', { ids, selected })),
  setAllSelection: (selected: boolean) =>
    request('/api/leads/select-all', json('PATCH', { selected })),
  selectNotEmailed: () =>
    request<{ selected?: number }>('/api/leads/select-not-emailed', { method: 'PATCH' }),

  setLlamada: (id: number, estado: LlamadaEstado) =>
    request(`/api/leads/${id}/llamada`, json('PATCH', { estado })),
  generar: (id: number, tipo: GeneracionTipo) =>
    request<{ guion?: string; maqueta?: string }>(`/api/leads/${id}/${tipo}`, { method: 'POST' }),

  getModelo: () => request<ModeloOportunidad>('/api/oportunidad'),
  calibrar: () => request<ModeloOportunidad>('/api/oportunidad/calibrar', { method: 'POST' }),
  restablecerModelo: () => request<ModeloOportunidad>('/api/oportunidad/calibrar', { method: 'DELETE' }),

  launch: (canal: Canal) => request<LaunchResult>(`/api/${canal}/launch`, { method: 'POST' }),

  async getQrBlob(): Promise<Blob> {
    const res = await fetch(`${API_URL}/api/whatsapp/qr?t=${Date.now()}`);
    if (!res.ok) throw new Error('QR no disponible');
    return res.blob();
  },
};

export const maquetaUrl = (archivo: string) =>
  `${API_URL}/maquetas/${encodeURIComponent(archivo)}`;
