import { CDSResponse, PatientScorecard } from './types';

const API_BASE = '/api';

export async function fetchLatestScorecards(): Promise<PatientScorecard[]> {
  try {
    const response = await fetch(`${API_BASE}/cds/scorecards/latest`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: CDSResponse = await response.json();
    return data.items || [];
  } catch (error) {
    console.error('Failed to fetch scorecards:', error);
    return [];
  }
}

export async function fetchPatientScorecard(patientId: string): Promise<PatientScorecard | null> {
  try {
    const response = await fetch(`${API_BASE}/cds/patient/${patientId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch patient ${patientId}:`, error);
    return null;
  }
}
