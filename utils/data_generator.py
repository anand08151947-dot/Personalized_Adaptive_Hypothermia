"""
Mocked Data Generator for AI-Based Personalized Adaptive Hypothermia System
Generates realistic physiological data for infants undergoing therapeutic hypothermia
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, List


class InfantPhysiologicalDataGenerator:
    """Generates realistic mocked physiological data for infants with HIE (Hypoxic-Ischemic Encephalopathy)"""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with optional random seed for reproducibility"""
        np.random.seed(seed)
        self.seed = seed
    
    def generate_baseline_parameters(self, patient_id: str) -> Dict:
        """Generate baseline physiological parameters for an individual patient"""
        
        # Baseline values for newborns with HIE (typically 3-5 kg, 48-55 cm)
        baseline = {
            'patient_id': patient_id,
            'birth_weight_kg': np.random.uniform(2.5, 4.5),
            'gestational_age_weeks': np.random.uniform(35, 42),
            'birth_hour': np.random.randint(0, 24),
            'hie_severity': np.random.choice(['mild', 'moderate', 'severe']),  # HIE classification
            
            # Baseline vitals (normal newborn ranges)
            'baseline_heart_rate': np.random.uniform(120, 160),  # bpm
            'baseline_resp_rate': np.random.uniform(40, 60),  # breaths/min
            'baseline_systolic_bp': np.random.uniform(50, 70),  # mmHg
            'baseline_diastolic_bp': np.random.uniform(30, 45),  # mmHg
            'baseline_oxygen_sat': np.random.uniform(95, 100),  # %
            
            # Rectal temperature baseline (normal newborn: 36.5-37.5°C)
            'baseline_rectal_temp': np.random.uniform(36.8, 37.4),  # °C
            'baseline_core_temp': np.random.uniform(36.5, 37.3),  # °C
            
            # Seizure susceptibility (depends on HIE severity)
            'seizure_risk_factor': {'mild': 0.1, 'moderate': 0.4, 'severe': 0.7}[
                np.random.choice(['mild', 'moderate', 'severe'])
            ],
        }
        return baseline
    
    def generate_cooling_protocol(self, hie_severity: str, baseline_temp: float) -> Dict:
        """Generate individualized cooling protocol based on HIE severity"""
        
        protocols = {
            'mild': {
                'target_temp': np.random.uniform(32.5, 33.5),  # °C
                'duration_hours': 48,
                'cooling_rate': np.random.uniform(0.1, 0.2),  # °C/hour
                'rewarming_rate': np.random.uniform(0.05, 0.1),  # °C/hour
            },
            'moderate': {
                'target_temp': np.random.uniform(33.0, 33.5),  # °C
                'duration_hours': 72,
                'cooling_rate': np.random.uniform(0.15, 0.25),  # °C/hour
                'rewarming_rate': np.random.uniform(0.05, 0.1),  # °C/hour
            },
            'severe': {
                'target_temp': np.random.uniform(32.0, 33.5),  # °C
                'duration_hours': 72,
                'cooling_rate': np.random.uniform(0.2, 0.3),  # °C/hour
                'rewarming_rate': np.random.uniform(0.05, 0.08),  # °C/hour
            },
        }
        
        protocol = protocols[hie_severity]
        protocol['baseline_temp'] = baseline_temp
        protocol['start_time'] = datetime.now()
        
        return protocol
    
    def simulate_rectal_temperature(
        self,
        baseline_temp: float,
        target_temp: float,
        cooling_rate: float,
        rewarming_rate: float,
        duration_minutes: int,
        time_step: int = 5  # 5-minute intervals
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate rectal temperature changes during cooling/rewarming
        
        Args:
            baseline_temp: Starting temperature
            target_temp: Target therapeutic temperature
            cooling_rate: Rate of cooling (°C/min)
            rewarming_rate: Rate of rewarming (°C/min)
            duration_minutes: Total duration
            time_step: Time interval for measurements (minutes)
        
        Returns:
            time_points: Array of time points
            temperatures: Array of temperatures at each time point
        """
        
        num_points = duration_minutes // time_step
        time_points = np.arange(0, duration_minutes, time_step)
        temperatures = np.zeros(len(time_points))
        
        # Phase 1: Cooling
        cooling_phase_minutes = abs(baseline_temp - target_temp) / (cooling_rate / 60)
        cooling_phase_steps = int(cooling_phase_minutes / time_step)
        
        current_temp = baseline_temp
        
        for i in range(len(time_points)):
            if i < cooling_phase_steps:
                # Cooling phase with slight overshoot
                current_temp = baseline_temp - (cooling_rate / 60 * time_points[i])
                # Add slight variability (±0.1°C)
                current_temp += np.random.normal(0, 0.05)
            else:
                # Maintenance phase - maintain target ±0.3°C
                current_temp = target_temp + np.random.normal(0, 0.15)
            
            # Ensure realistic bounds
            current_temp = np.clip(current_temp, target_temp - 0.5, baseline_temp + 0.5)
            temperatures[i] = current_temp
        
        return time_points, temperatures
    
    def generate_heart_rate_data(
        self,
        baseline_hr: float,
        duration_minutes: int,
        time_step: int = 5,
        stress_level: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate heart rate variations during hypothermia
        Hypothermia typically causes bradycardia (lower HR)
        """
        
        num_points = duration_minutes // time_step
        time_points = np.arange(0, duration_minutes, time_step)
        heart_rates = np.zeros(len(time_points))
        
        # During hypothermia, HR typically decreases by 10-20%
        hypothermia_effect = np.random.uniform(0.85, 0.95)
        
        for i in range(len(time_points)):
            # Base HR reduction during cooling
            base_hr = baseline_hr * hypothermia_effect
            
            # Add variability and stress factors
            noise = np.random.normal(0, 5)  # ±5 bpm variability
            stress_component = stress_level * np.sin(2 * np.pi * i / (60 * 60 / time_step))  # Cyclic stress
            
            hr = base_hr + noise + stress_component
            heart_rates[i] = np.clip(hr, 80, 180)  # Realistic bounds for newborn
        
        return time_points, heart_rates
    
    def generate_blood_pressure_data(
        self,
        baseline_systolic: float,
        baseline_diastolic: float,
        duration_minutes: int,
        time_step: int = 5
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate systolic and diastolic blood pressure during hypothermia
        Hypothermia can cause initial hypertension, then hypotension
        """
        
        num_points = duration_minutes // time_step
        time_points = np.arange(0, duration_minutes, time_step)
        systolic_bp = np.zeros(len(time_points))
        diastolic_bp = np.zeros(len(time_points))
        
        for i in range(len(time_points)):
            # BP trend: slight decrease during cooling
            trend = 0.95 + 0.1 * np.sin(2 * np.pi * i / (120 * 60 / time_step))
            
            sys_bp = baseline_systolic * trend + np.random.normal(0, 3)
            dia_bp = baseline_diastolic * trend + np.random.normal(0, 2)
            
            systolic_bp[i] = np.clip(sys_bp, 40, 80)
            diastolic_bp[i] = np.clip(dia_bp, 20, 50)
        
        return time_points, systolic_bp, diastolic_bp
    
    def generate_oxygen_saturation_data(
        self,
        baseline_spo2: float,
        duration_minutes: int,
        time_step: int = 5,
        respiratory_distress: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate oxygen saturation (SpO2) during therapeutic hypothermia
        """
        
        num_points = duration_minutes // time_step
        time_points = np.arange(0, duration_minutes, time_step)
        spo2_values = np.zeros(len(time_points))
        
        for i in range(len(time_points)):
            base_spo2 = baseline_spo2
            
            if respiratory_distress:
                # Add dips in SpO2 (15-30 min intervals)
                if (i % (20 * 60 / time_step) < 10 * 60 / time_step):
                    base_spo2 -= np.random.uniform(2, 5)
            
            # Normal variability
            spo2 = base_spo2 + np.random.normal(0, 0.5)
            spo2_values[i] = np.clip(spo2, 92, 100)
        
        return time_points, spo2_values
    
    def generate_eeg_data(
        self,
        duration_minutes: int,
        time_step: int = 1,  # Higher frequency for EEG (1-second intervals)
        seizure_probability: float = 0.2,
        seizure_start_minute: int = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate simplified EEG data (frequency bands: delta, theta, alpha)
        Returns power in each band (in microvolts^2)
        """
        
        num_points = duration_minutes * 60 // time_step  # Convert to seconds
        time_points = np.arange(0, duration_minutes * 60, time_step)
        
        # EEG frequency bands (simplified)
        delta_power = np.zeros(len(time_points))  # 0.5-4 Hz
        theta_power = np.zeros(len(time_points))  # 4-8 Hz
        alpha_power = np.zeros(len(time_points))  # 8-13 Hz
        
        seizure_active = False
        
        for i in range(len(time_points)):
            current_minute = time_points[i] / 60
            
            # Check for seizure onset
            if seizure_start_minute is None and np.random.random() < seizure_probability / (duration_minutes * 60):
                seizure_start_minute = current_minute
            
            if seizure_start_minute is not None:
                seizure_duration = 2  # 2-minute seizure
                if current_minute < seizure_start_minute + seizure_duration:
                    seizure_active = True
                else:
                    seizure_active = False
                    seizure_start_minute = None
            
            if seizure_active:
                # During seizure: high-frequency activity
                delta_power[i] = np.random.uniform(50, 150)
                theta_power[i] = np.random.uniform(100, 250)
                alpha_power[i] = np.random.uniform(200, 400)
            else:
                # Normal EEG during hypothermia (slowed activity)
                delta_power[i] = np.random.uniform(10, 40)
                theta_power[i] = np.random.uniform(5, 20)
                alpha_power[i] = np.random.uniform(2, 10)
        
        return time_points, delta_power, theta_power, alpha_power
    
    def generate_blood_gas_data(
        self,
        duration_hours: int,
        time_step_hours: int = 4,
        hie_severity: str = 'moderate'
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate arterial blood gas (ABG) measurements
        Returns pH, pCO2, pO2, lactate levels
        """
        
        num_points = duration_hours // time_step_hours
        time_points = np.arange(0, duration_hours, time_step_hours)
        
        # Normal newborn ABG values
        pH_values = np.zeros(num_points)
        pco2_values = np.zeros(num_points)
        po2_values = np.zeros(num_points)
        lactate_values = np.zeros(num_points)
        
        # Baseline depends on HIE severity
        baselines = {
            'mild': {'pH': 7.35, 'pCO2': 45, 'pO2': 85, 'lactate': 2},
            'moderate': {'pH': 7.30, 'pCO2': 48, 'pO2': 75, 'lactate': 4},
            'severe': {'pH': 7.25, 'pCO2': 50, 'pO2': 65, 'lactate': 8},
        }
        
        baseline = baselines[hie_severity]
        
        for i in range(num_points):
            # Gradual improvement over time with hypothermia
            improvement_factor = 1 - (0.01 * i)  # Slow improvement
            
            pH_values[i] = baseline['pH'] + np.random.uniform(-0.05, 0.1) * improvement_factor
            pco2_values[i] = baseline['pCO2'] + np.random.uniform(-5, 3) * improvement_factor
            po2_values[i] = baseline['pO2'] + np.random.uniform(-10, 15) * improvement_factor
            lactate_values[i] = baseline['lactate'] * (0.9 ** i) + np.random.uniform(-0.5, 0.5)
        
        return time_points, pH_values, pco2_values, po2_values, lactate_values
    
    def generate_complete_patient_dataset(
        self,
        patient_id: str,
        duration_hours: int = 72,
        time_step_minutes: int = 5
    ) -> pd.DataFrame:
        """
        Generate a complete dataset for one patient during therapeutic hypothermia
        """
        
        # Generate baseline parameters
        baseline_params = self.generate_baseline_parameters(patient_id)
        
        # Generate individualized protocol
        protocol = self.generate_cooling_protocol(
            baseline_params['hie_severity'],
            baseline_params['baseline_rectal_temp']
        )
        
        duration_minutes = duration_hours * 60
        
        # Generate vital signs
        time_points_vitals, rectal_temps = self.simulate_rectal_temperature(
            protocol['baseline_temp'],
            protocol['target_temp'],
            protocol['cooling_rate'] / 60,  # Convert to °C/min
            protocol['rewarming_rate'] / 60,
            duration_minutes,
            time_step_minutes
        )
        
        _, heart_rates = self.generate_heart_rate_data(
            baseline_params['baseline_heart_rate'],
            duration_minutes,
            time_step_minutes,
            stress_level=0.5
        )
        
        _, systolic_bp, diastolic_bp = self.generate_blood_pressure_data(
            baseline_params['baseline_systolic_bp'],
            baseline_params['baseline_diastolic_bp'],
            duration_minutes,
            time_step_minutes
        )
        
        _, spo2 = self.generate_oxygen_saturation_data(
            baseline_params['baseline_oxygen_sat'],
            duration_minutes,
            time_step_minutes,
            respiratory_distress=baseline_params['hie_severity'] == 'severe'
        )
        
        # Create base dataframe with 5-minute intervals
        df = pd.DataFrame({
            'patient_id': patient_id,
            'time_minutes': time_points_vitals,
            'time_hours': time_points_vitals / 60,
            'rectal_temperature_c': rectal_temps,
            'heart_rate_bpm': heart_rates,
            'systolic_bp_mmhg': systolic_bp,
            'diastolic_bp_mmhg': diastolic_bp,
            'oxygen_saturation_percent': spo2,
            'hie_severity': baseline_params['hie_severity'],
            'target_temp_c': protocol['target_temp'],
        })
        
        # Add blood gas data (every 4 hours)
        time_points_abg, pH, pco2, po2, lactate = self.generate_blood_gas_data(
            duration_hours,
            time_step_hours=4,
            hie_severity=baseline_params['hie_severity']
        )
        
        # Merge ABG data at appropriate times
        abg_df = pd.DataFrame({
            'time_hours': time_points_abg,
            'pH': pH,
            'pCO2_mmhg': pco2,
            'pO2_mmhg': po2,
            'lactate_mmol': lactate
        })
        
        # Forward-fill ABG values to match 5-minute intervals
        df['time_hours_abg'] = df['time_hours']
        df = df.merge(abg_df, left_on='time_hours_abg', right_on='time_hours', how='left')
        df[['pH', 'pCO2_mmhg', 'pO2_mmhg', 'lactate_mmol']] = \
            df[['pH', 'pCO2_mmhg', 'pO2_mmhg', 'lactate_mmol']].fillna(method='ffill')
        df = df.drop('time_hours_abg', axis=1)
        
        # Add patient baseline info as columns
        for key, value in baseline_params.items():
            if key != 'patient_id':
                df[f'baseline_{key}'] = value
        
        return df
    
    def generate_batch_dataset(
        self,
        num_patients: int = 100,
        duration_hours: int = 72
    ) -> pd.DataFrame:
        """Generate dataset for multiple patients"""
        
        datasets = []
        for i in range(num_patients):
            patient_id = f'PATIENT_{i+1:04d}'
            print(f"Generating data for {patient_id}...")
            
            patient_df = self.generate_complete_patient_dataset(
                patient_id,
                duration_hours=duration_hours
            )
            datasets.append(patient_df)
        
        combined_df = pd.concat(datasets, ignore_index=True)
        return combined_df


# Example usage
if __name__ == "__main__":
    generator = InfantPhysiologicalDataGenerator(seed=42)
    
    # Generate single patient dataset
    print("Generating single patient dataset...")
    single_patient_df = generator.generate_complete_patient_dataset(
        patient_id='PATIENT_0001',
        duration_hours=72
    )
    
    print(f"Dataset shape: {single_patient_df.shape}")
    print(f"\nFirst few rows:\n{single_patient_df.head()}")
    print(f"\nDataset info:\n{single_patient_df.info()}")
    print(f"\nBasic statistics:\n{single_patient_df.describe()}")
