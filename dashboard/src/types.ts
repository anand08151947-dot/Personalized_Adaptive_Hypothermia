export interface Probabilities {
  seizure: number | null;
  sepsis: number | null;
  cardiac: number | null;
  renal: number | null;
  prognosis_poor_outcome: number | null;
}

export interface RiskLevels {
  seizure: 'HIGH' | 'MED' | 'LOW';
  sepsis: 'HIGH' | 'MED' | 'LOW';
  cardiac: 'HIGH' | 'MED' | 'LOW';
  renal: 'HIGH' | 'MED' | 'LOW';
  prognosis: 'HIGH' | 'MED' | 'LOW';
}

export interface PatientScorecard {
  patient_id: string;
  timestamp: string;
  probabilities: Probabilities;
  risk_levels: RiskLevels;
  temperature_adjustment_degC: number;
  recommendations: string[];
}

export interface CDSResponse {
  generated_at: string;
  items: PatientScorecard[];
}
