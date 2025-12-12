import React, { useState } from 'react';
import { PatientScorecard } from '../types';
import { AlertCircle, Activity, Heart, Droplet, Brain, Thermometer } from 'lucide-react';

interface Props {
  scorecard: PatientScorecard;
  onRiskClick?: (riskType: 'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis') => void;
}

const getRiskColor = (risk: 'HIGH' | 'MED' | 'LOW'): string => {
  switch (risk) {
    case 'HIGH': return '#ef4444';
    case 'MED': return '#f59e0b';
    case 'LOW': return '#10b981';
  }
};

const getRiskBg = (risk: 'HIGH' | 'MED' | 'LOW'): string => {
  switch (risk) {
    case 'HIGH': return '#fee2e2';
    case 'MED': return '#fef3c7';
    case 'LOW': return '#d1fae5';
  }
};

interface RiskBadgeProps {
  label: string;
  risk: 'HIGH' | 'MED' | 'LOW';
  icon: React.ReactNode;
  riskType: 'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis';
  onClick?: (riskType: 'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis') => void;
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ label, risk, icon, riskType, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onClick={() => onClick?.(riskType)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        borderRadius: '8px',
        backgroundColor: getRiskBg(risk),
        border: `2px solid ${getRiskColor(risk)}`,
        cursor: 'pointer',
        transition: 'all 0.2s',
        transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
        boxShadow: isHovered ? '0 4px 12px rgba(0,0,0,0.15)' : 'none'
      }}
    >
      <span style={{ color: getRiskColor(risk) }}>{icon}</span>
      <div>
        <div style={{ fontSize: '11px', opacity: 0.7, textTransform: 'uppercase', fontWeight: 600 }}>{label}</div>
        <div style={{ fontSize: '14px', fontWeight: 700, color: getRiskColor(risk) }}>{risk}</div>
      </div>
    </div>
  );
};

export const PatientCard: React.FC<Props> = ({ scorecard, onRiskClick }) => {
  const { patient_id, risk_levels, temperature_adjustment_degC, recommendations, timestamp } = scorecard;
  
  const hasHighRisk = Object.values(risk_levels).some(r => r === 'HIGH');
  const hasMedRisk = Object.values(risk_levels).some(r => r === 'MED');

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      border: hasHighRisk ? '3px solid #ef4444' : hasMedRisk ? '2px solid #f59e0b' : '1px solid #e5e7eb'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#1f2937' }}>
          {patient_id}
        </h3>
        <div style={{ fontSize: '12px', color: '#6b7280' }}>
          {new Date(timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* Risk Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '10px',
        marginBottom: '16px'
      }}>
        <RiskBadge label="Seizure" risk={risk_levels.seizure} icon={<Brain size={18} />} riskType="seizure" onClick={onRiskClick} />
        <RiskBadge label="Sepsis" risk={risk_levels.sepsis} icon={<Activity size={18} />} riskType="sepsis" onClick={onRiskClick} />
        <RiskBadge label="Cardiac" risk={risk_levels.cardiac} icon={<Heart size={18} />} riskType="cardiac" onClick={onRiskClick} />
        <RiskBadge label="Renal" risk={risk_levels.renal} icon={<Droplet size={18} />} riskType="renal" onClick={onRiskClick} />
        <RiskBadge label="Prognosis" risk={risk_levels.prognosis} icon={<AlertCircle size={18} />} riskType="prognosis" onClick={onRiskClick} />
      </div>

      {/* Temperature Adjustment */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '12px',
        backgroundColor: temperature_adjustment_degC > 0.5 ? '#fef3c7' : '#f0fdf4',
        borderRadius: '8px',
        marginBottom: '16px'
      }}>
        <Thermometer size={20} color={temperature_adjustment_degC > 0.5 ? '#f59e0b' : '#10b981'} />
        <div>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280' }}>Temperature Adjustment</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#1f2937' }}>
            {temperature_adjustment_degC > 0 ? '-' : ''}{temperature_adjustment_degC.toFixed(1)}°C
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div>
        <div style={{ fontSize: '13px', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>
          Clinical Recommendations:
        </div>
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          {recommendations.map((rec, idx) => (
            <li key={idx} style={{ fontSize: '13px', color: '#374151', marginBottom: '4px' }}>
              {rec}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
