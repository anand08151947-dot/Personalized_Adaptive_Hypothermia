import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { PatientScorecard } from '../types';

interface Props {
  scorecard: PatientScorecard;
}

const getRiskColor = (risk: 'HIGH' | 'MED' | 'LOW'): string => {
  switch (risk) {
    case 'HIGH': return '#ef4444';
    case 'MED': return '#f59e0b';
    case 'LOW': return '#10b981';
  }
};

export const RiskChart: React.FC<Props> = ({ scorecard }) => {
  const data = [
    {
      name: 'Seizure',
      probability: (scorecard.probabilities.seizure || 0) * 100,
      risk: scorecard.risk_levels.seizure
    },
    {
      name: 'Sepsis',
      probability: (scorecard.probabilities.sepsis || 0) * 100,
      risk: scorecard.risk_levels.sepsis
    },
    {
      name: 'Cardiac',
      probability: (scorecard.probabilities.cardiac || 0) * 100,
      risk: scorecard.risk_levels.cardiac
    },
    {
      name: 'Renal',
      probability: (scorecard.probabilities.renal || 0) * 100,
      risk: scorecard.risk_levels.renal
    },
    {
      name: 'Poor Outcome',
      probability: (scorecard.probabilities.prognosis_poor_outcome || 0) * 100,
      risk: scorecard.risk_levels.prognosis
    }
  ];

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginTop: '20px'
    }}>
      <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#1f2937', marginBottom: '16px' }}>
        Risk Probabilities - {scorecard.patient_id}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
          <Legend />
          <Bar dataKey="probability" name="Risk Probability">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getRiskColor(entry.risk)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
