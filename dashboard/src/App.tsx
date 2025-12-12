import React, { useState, useEffect } from 'react';
import { PatientScorecard } from './types';
import { fetchLatestScorecards } from './api';
import { PatientCard } from './components/PatientCard';
import { RiskChart } from './components/RiskChart';
import { RiskDetailModal } from './components/RiskDetailModal';
import { Activity, RefreshCw } from 'lucide-react';
import './index.css';

const App: React.FC = () => {
  const [scorecards, setScorecards] = useState<PatientScorecard[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);
  const [selectedRisk, setSelectedRisk] = useState<'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis' | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadData = async () => {
    setLoading(true);
    const data = await fetchLatestScorecards();
    setScorecards(data);
    setLastUpdate(new Date());
    if (data.length > 0 && !selectedPatient) {
      setSelectedPatient(data[0].patient_id);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const selectedScorecard = scorecards.find(s => s.patient_id === selectedPatient);

  const highRiskCount = scorecards.filter(s =>
    Object.values(s.risk_levels).some(r => r === 'HIGH')
  ).length;

  const handleRiskClick = (riskType: 'seizure' | 'sepsis' | 'cardiac' | 'renal' | 'prognosis') => {
    setSelectedRisk(riskType);
    setIsModalOpen(true);
  };

  return (
    <div style={{ minHeight: '100vh', padding: '20px' }}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Activity size={32} color="#667eea" />
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1f2937', margin: 0 }}>
                Hypothermia Clinical Decision Support
              </h1>
              <p style={{ fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' }}>
                Real-time patient monitoring and risk assessment
              </p>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <button
              onClick={loadData}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                backgroundColor: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                opacity: loading ? 0.6 : 1
              }}
            >
              <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
              Refresh
            </button>
            {lastUpdate && (
              <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
                Last update: {lastUpdate.toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>

        {/* Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginTop: '20px'
        }}>
          <div style={{ padding: '12px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>Total Patients</div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#10b981' }}>{scorecards.length}</div>
          </div>
          <div style={{ padding: '12px', backgroundColor: '#fee2e2', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>High Risk Alerts</div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#ef4444' }}>{highRiskCount}</div>
          </div>
          <div style={{ padding: '12px', backgroundColor: '#ede9fe', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>System Status</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#8b5cf6' }}>
              {loading ? 'Updating...' : 'Active'}
            </div>
          </div>
        </div>
      </div>

      {loading && scorecards.length === 0 ? (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          color: '#6b7280'
        }}>
          Loading patient data...
        </div>
      ) : scorecards.length === 0 ? (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          color: '#6b7280'
        }}>
          No patient data available. Ensure the API server is running.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Patient List */}
          <div>
            <h2 style={{ color: 'white', fontSize: '18px', fontWeight: 700, marginBottom: '12px' }}>
              Active Patients
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {scorecards.map(scorecard => (
                <div
                  key={scorecard.patient_id}
                  onClick={() => setSelectedPatient(scorecard.patient_id)}
                  style={{
                    cursor: 'pointer',
                    opacity: selectedPatient === scorecard.patient_id ? 1 : 0.8,
                    transform: selectedPatient === scorecard.patient_id ? 'scale(1.02)' : 'scale(1)',
                    transition: 'all 0.2s'
                  }}
                >
                  <PatientCard scorecard={scorecard} onRiskClick={handleRiskClick} />
                </div>
              ))}
            </div>
          </div>

          {/* Detail View */}
          <div>
            <h2 style={{ color: 'white', fontSize: '18px', fontWeight: 700, marginBottom: '12px' }}>
              Detailed Analysis
            </h2>
            {selectedScorecard && (
              <RiskChart scorecard={selectedScorecard} />
            )}
          </div>
        </div>
      )}

      <RiskDetailModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        riskType={selectedRisk}
        scorecard={selectedScorecard || scorecards[0]}
      />

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default App;
