import React from 'react';
import { X, AlertCircle, TrendingUp, CheckCircle } from 'lucide-react';
import { PatientScorecard } from '../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  riskType: 'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis' | null;
  scorecard: PatientScorecard;
}

const RISK_DETAILS = {
  seizure: {
    title: 'Seizure Risk',
    description: 'Probability of seizure occurrence in therapeutic hypothermia patient',
    highThreshold: 0.70,
    mediumThreshold: 0.40,
    icon: '🧠',
    interpretation: {
      HIGH: 'High risk of seizure activity. Immediate intervention required.',
      MED: 'Moderate risk. Enhanced monitoring recommended.',
      LOW: 'Low risk. Routine monitoring sufficient.'
    },
    actions: {
      HIGH: [
        'Initiate continuous EEG monitoring',
        'Review and optimize antiseizure medications',
        'Prepare emergency seizure protocol',
        'Alert neurology team',
        'Ensure IV access and emergency meds available'
      ],
      MED: [
        'Increase frequency of neurological assessments',
        'Consider EEG if symptomatic',
        'Review current antiseizure therapy',
        'Prepare seizure management supplies'
      ],
      LOW: [
        'Continue routine neuro checks',
        'Maintain current medication regimen',
        'Monitor for any symptom changes'
      ]
    }
  },
  sepsis: {
    title: 'Sepsis Risk',
    description: 'Probability of sepsis development during hypothermia management',
    highThreshold: 0.65,
    mediumThreshold: 0.35,
    icon: '🦠',
    interpretation: {
      HIGH: 'High sepsis risk. Implement full infection control protocol.',
      MED: 'Moderate risk. Enhanced surveillance and preventive measures needed.',
      LOW: 'Low risk. Standard infection prevention protocols.'
    },
    actions: {
      HIGH: [
        'Obtain blood cultures immediately',
        'Start broad-spectrum antibiotics per protocol',
        'Administer IV fluids per sepsis bundle',
        'Monitor lactate and CBC closely',
        'Place central line if needed for monitoring'
      ],
      MED: [
        'Trend lactate levels every 4-6 hours',
        'Monitor vital signs and organ function closely',
        'Maintain strict hand hygiene and sterile technique',
        'Review antibiotic prophylaxis'
      ],
      LOW: [
        'Continue standard infection prevention',
        'Monitor temperature and WBC trends',
        'Maintain hygiene protocols'
      ]
    }
  },
  cardiac: {
    title: 'Cardiac Risk',
    description: 'Probability of cardiac complications during hypothermia',
    highThreshold: 0.60,
    mediumThreshold: 0.30,
    icon: '❤️',
    interpretation: {
      HIGH: 'High cardiac risk. Close hemodynamic monitoring essential.',
      MED: 'Moderate risk. Enhanced cardiac surveillance required.',
      LOW: 'Low risk. Routine cardiac monitoring sufficient.'
    },
    actions: {
      HIGH: [
        'Cardiology consultation',
        'Continuous telemetry monitoring',
        'Optimize MAP: target 65-75 mmHg',
        'Monitor QT interval closely',
        'Review QT-prolonging medications',
        'Prepare for potential ECMO/IABP'
      ],
      MED: [
        'Increase telemetry vigilance',
        'Review medications affecting QT/blood pressure',
        'Monitor heart rate and rhythm changes',
        'Assess volume status regularly'
      ],
      LOW: [
        'Standard cardiac monitoring',
        'Routine vital sign checks',
        'Continue current management'
      ]
    }
  },
  renal: {
    title: 'Renal Risk',
    description: 'Probability of acute kidney injury during hypothermia treatment',
    highThreshold: 0.60,
    mediumThreshold: 0.30,
    icon: '🫘',
    interpretation: {
      HIGH: 'High AKI risk. Aggressive renal protection and monitoring needed.',
      MED: 'Moderate risk. Enhanced renal function surveillance recommended.',
      LOW: 'Low risk. Standard renal monitoring appropriate.'
    },
    actions: {
      HIGH: [
        'Nephrology consultation',
        'Avoid nephrotoxic medications',
        'Optimize fluid balance',
        'Monitor urine output hourly',
        'Check creatinine and BUN daily',
        'Consider renal replacement therapy prep'
      ],
      MED: [
        'Monitor urine output and color',
        'Check creatinine every 24 hours',
        'Adjust medication dosing for renal function',
        'Maintain appropriate fluid balance'
      ],
      LOW: [
        'Routine renal function monitoring',
        'Standard medication dosing',
        'Monitor fluid intake/output'
      ]
    }
  },
  prognosis: {
    title: 'Neurological Prognosis',
    description: 'Probability of poor 72-hour neurological outcome',
    highThreshold: 0.65,
    mediumThreshold: 0.40,
    icon: '🔮',
    interpretation: {
      HIGH: 'High risk of poor neurological outcome. Consider advanced support.',
      MED: 'Moderate risk. Multidisciplinary review and reassessment needed.',
      LOW: 'Low risk of poor outcome. Continue current management.'
    },
    actions: {
      HIGH: [
        'Multidisciplinary case conference',
        'Discuss goals of care with family',
        'Consider advanced neuromonitoring',
        'Review neuroprotective strategies',
        'Consider long-term care planning',
        'Evaluate for clinical trials'
      ],
      MED: [
        'Ensure multidisciplinary team involvement',
        'Reassess goals and trajectory in 12 hours',
        'Optimize all neuroprotective therapies',
        'Plan family updates and discussions'
      ],
      LOW: [
        'Continue current protective measures',
        'Plan for progressive rehabilitation',
        'Prepare discharge/transition plans'
      ]
    }
  }
};

export const RiskDetailModal: React.FC<Props> = ({ isOpen, onClose, riskType, scorecard }) => {
  if (!isOpen || !riskType) return null;

  const risk = RISK_DETAILS[riskType];
  const riskLevel = scorecard.risk_levels[riskType === 'prognosis' ? 'prognosis' : riskType];
  let probability = scorecard.probabilities[riskType === 'prognosis' ? 'prognosis_poor_outcome' : riskType];

  const getRiskColor = (level: 'HIGH' | 'MED' | 'LOW') => {
    switch (level) {
      case 'HIGH': return '#ef4444';
      case 'MED': return '#f59e0b';
      case 'LOW': return '#10b981';
    }
  };

  const getRiskBgColor = (level: 'HIGH' | 'MED' | 'LOW') => {
    switch (level) {
      case 'HIGH': return '#fee2e2';
      case 'MED': return '#fef3c7';
      case 'LOW': return '#d1fae5';
    }
  };

  const actions = risk.actions[riskLevel];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 20px 25px rgba(0,0,0,0.15)',
        animation: 'slideUp 0.3s ease-out'
      }}>
        {/* Header */}
        <div style={{
          padding: '24px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '32px' }}>{risk.icon}</span>
            <div>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: '#1f2937' }}>
                {risk.title}
              </h2>
              <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#6b7280' }}>
                {risk.description}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px'
            }}
          >
            <X size={24} color="#6b7280" />
          </button>
        </div>

        {/* Risk Level Section */}
        <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb', backgroundColor: getRiskBgColor(riskLevel) }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Current Risk */}
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>
                Current Risk Level
              </div>
              <div style={{
                fontSize: '28px',
                fontWeight: 700,
                color: getRiskColor(riskLevel),
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                {riskLevel}
                {riskLevel === 'HIGH' && <AlertCircle size={24} />}
                {riskLevel === 'MED' && <TrendingUp size={24} />}
                {riskLevel === 'LOW' && <CheckCircle size={24} />}
              </div>
            </div>

            {/* Probability */}
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>
                Event Probability
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: '#1f2937' }}>
                {probability !== null ? `${(probability * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
          </div>

          {/* Thresholds */}
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>
              Risk Thresholds
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ padding: '8px 12px', backgroundColor: '#fee2e2', borderRadius: '6px', fontSize: '13px' }}>
                <span style={{ color: '#6b7280' }}>HIGH: </span>
                <span style={{ color: '#ef4444', fontWeight: 600 }}>&ge;{(risk.highThreshold * 100).toFixed(0)}%</span>
              </div>
              <div style={{ padding: '8px 12px', backgroundColor: '#fef3c7', borderRadius: '6px', fontSize: '13px' }}>
                <span style={{ color: '#6b7280' }}>MED: </span>
                <span style={{ color: '#f59e0b', fontWeight: 600 }}>&ge;{(risk.mediumThreshold * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Clinical Interpretation */}
        <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>
            Clinical Interpretation
          </div>
          <div style={{
            padding: '12px',
            backgroundColor: '#f9fafb',
            borderLeft: `4px solid ${getRiskColor(riskLevel)}`,
            borderRadius: '6px',
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#374151'
          }}>
            {risk.interpretation[riskLevel]}
          </div>
        </div>

        {/* Recommended Actions */}
        <div style={{ padding: '24px' }}>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#6b7280', marginBottom: '12px' }}>
            Recommended Clinical Actions
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {actions.map((action, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '13px',
                  color: '#374151',
                  marginBottom: '10px',
                  paddingLeft: '8px',
                  lineHeight: '1.5'
                }}
              >
                {action}
              </li>
            ))}
          </ul>
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          backgroundColor: '#f9fafb',
          borderTop: '1px solid #e5e7eb',
          textAlign: 'right'
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px'
            }}
          >
            Close
          </button>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};
