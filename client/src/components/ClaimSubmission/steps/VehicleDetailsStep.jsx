import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * VehicleDetailsStep - Step 2
 * Enter vehicle details
 */
export default function VehicleDetailsStep({ formData, onNext, onPrevious }) {
  const [vehicleModel, setVehicleModel] = useState(formData.vehicleModel || '');
  const [vehicleNumber, setVehicleNumber] = useState(formData.vehicleNumber || '');
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!vehicleModel.trim()) {
      setError('Please enter your vehicle model');
      return;
    }
    if (!vehicleNumber.trim()) {
      setError('Please enter your vehicle registration number');
      return;
    }
    onNext({
      vehicleModel,
      vehicleNumber
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Vehicle Details</h2>
        <p className="step-description">
          Enter your vehicle information
        </p>
      </div>

      <div className="step-content">
        {/* Vehicle Model */}
        <div className="form-section">
          <label htmlFor="vehicleModel" className="form-section-title">🚗 Vehicle Model</label>
          <input
            type="text"
            id="vehicleModel"
            className="policy-name-input"
            placeholder="e.g., Honda City, Maruti Swift, Hero Splendor, Ashok Leyland"
            value={vehicleModel}
            onChange={(e) => setVehicleModel(e.target.value)}
          />
          <p className="policy-help-text">
            Enter the make and model of your vehicle
          </p>
        </div>

        {/* Vehicle Registration Number */}
        <div className="form-section">
          <label htmlFor="vehicleNumber" className="form-section-title">Vehicle Registration Number</label>
          <input
            type="text"
            id="vehicleNumber"
            className="policy-name-input"
            placeholder="e.g., MH-02-AB-1234"
            value={vehicleNumber}
            onChange={(e) => setVehicleNumber(e.target.value.toUpperCase())}
          />
          <p className="policy-help-text">
            Enter your vehicle's registration/license plate number
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            {/* <span className="alert-icon">❌</span> */}
            <span className="alert-text">{error}</span>
          </div>
        )}
      </div>

      {/* Step Footer */}
      <div className="step-footer">
        <button className="btn btn-secondary" onClick={onPrevious}>
          ← Previous
        </button>
        <button
          className="btn btn-primary"
          onClick={handleNext}
        >
          Next Step
          <span className="btn-icon">→</span>
        </button>
      </div>
    </div>
  );
}
