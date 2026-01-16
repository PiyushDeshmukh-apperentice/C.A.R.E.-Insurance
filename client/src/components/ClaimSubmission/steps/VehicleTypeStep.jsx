import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * VehicleTypeStep - Step 1
 * Select vehicle type and enter policy name
 */
export default function VehicleTypeStep({ formData, onNext, onCancel }) {
  const [vehicleType, setVehicleType] = useState(formData.vehicleType || '');
  const [policyName, setPolicyName] = useState(formData.policyName || '');
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!vehicleType) {
      setError('Please select a vehicle type');
      return;
    }
    if (!policyName.trim()) {
      setError('Please enter your policy name');
      return;
    }
    onNext({
      vehicleType,
      policyName
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Vehicle Insurance Claim</h2>
        <p className="step-description">
          Select your vehicle type and provide your policy details
        </p>
      </div>

      <div className="step-content">
        {/* Policy Name Section - FIRST */}
        <div className="form-section policy-name-section">
          <label htmlFor="policyName" className="form-section-title">Your Policy Name</label>
          <input
            type="text"
            id="policyName"
            className="policy-name-input"
            placeholder="Enter your insurance policy name"
            value={policyName}
            onChange={(e) => setPolicyName(e.target.value)}
          />
          <p className="policy-help-text">
            Example: "Two Wheeler Premium", "Car Comprehensive", "Vehicle Master Plus"
          </p>
        </div>

        {/* Vehicle Type Selection */}
        <div className="form-section">
          <label className="form-section-title">Vehicle Type</label>
          <div className="radio-group">
            {/* Car Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="car"
                name="vehicleType"
                value="car"
                checked={vehicleType === 'car'}
                onChange={(e) => setVehicleType(e.target.value)}
              />
              <label htmlFor="car" className="radio-label">
                {/* <span className="radio-icon">🚗</span> */}
                <span className="radio-content">
                  <span className="radio-title">Four Wheeler (Car)</span>
                  <span className="radio-desc">Sedan, SUV, or any 4-wheeler vehicle</span>
                </span>
              </label>
            </div>

            {/* Bike Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="bike"
                name="vehicleType"
                value="bike"
                checked={vehicleType === 'bike'}
                onChange={(e) => setVehicleType(e.target.value)}
              />
              <label htmlFor="bike" className="radio-label">
                {/* <span className="radio-icon">🏍️</span> */}
                <span className="radio-content">
                  <span className="radio-title">Motorcycle/Bike</span>
                  <span className="radio-desc">Two-wheeler motorcycle or bike</span>
                </span>
              </label>
            </div>

            {/* Scooter Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="scooter"
                name="vehicleType"
                value="scooter"
                checked={vehicleType === 'scooter'}
                onChange={(e) => setVehicleType(e.target.value)}
              />
              <label htmlFor="scooter" className="radio-label">
                {/* <span className="radio-icon">🛵</span> */}
                <span className="radio-content">
                  <span className="radio-title">Scooter/Scooty</span>
                  <span className="radio-desc">Two-wheeler scooter or scooty</span>
                </span>
              </label>
            </div>

            {/* Truck Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="truck"
                name="vehicleType"
                value="truck"
                checked={vehicleType === 'truck'}
                onChange={(e) => setVehicleType(e.target.value)}
              />
              <label htmlFor="truck" className="radio-label">
                {/* <span className="radio-icon">🚚</span> */}
                <span className="radio-content">
                  <span className="radio-title">Truck/Heavy Vehicle</span>
                  <span className="radio-desc">Commercial truck or heavy vehicle</span>
                </span>
              </label>
            </div>
          </div>
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
        <button className="btn btn-secondary" onClick={onCancel}>
          Cancel
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
