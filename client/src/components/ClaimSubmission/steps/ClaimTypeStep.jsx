import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * ClaimTypeStep - Step 1
 * Select claim type (Cashless/Reimbursement) and accident status
 */
export default function ClaimTypeStep({ formData, onNext, onCancel }) {
  const [claimType, setClaimType] = useState(formData.claimType || '');
  const [isAccident, setIsAccident] = useState(formData.isAccident || false);
  const [policyName, setPolicyName] = useState(formData.policyName || '');
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!claimType) {
      setError('Please select a claim type');
      return;
    }
    if (!policyName.trim()) {
      setError('Please enter your policy name');
      return;
    }
    onNext({
      claimType,
      isAccident,
      policyName
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Health Claim Information</h2>
        <p className="step-description">
          Please provide your policy details and claim information
        </p>
      </div>

      <div className="step-content">
        {/* Policy Name Section - FIRST */}
        <div className="form-section policy-name-section">
          <label htmlFor="policyName" className="form-section-title">📋 Your Policy Name</label>
          <input
            type="text"
            id="policyName"
            className="policy-name-input"
            placeholder="Enter your insurance policy name"
            value={policyName}
            onChange={(e) => setPolicyName(e.target.value)}
          />
          <p className="policy-help-text">
            Example: "Health Plus Premium", "Family Mediclaim", "Golden Health Plan"
          </p>
        </div>

        {/* Claim Type Selection */}
        <div className="form-section">
          <label className="form-section-title">Claim Type</label>
          <div className="radio-group">
            {/* Cashless Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="cashless"
                name="claimType"
                value="cashless"
                checked={claimType === 'cashless'}
                onChange={(e) => setClaimType(e.target.value)}
              />
              <label htmlFor="cashless" className="radio-label">
                {/* <span className="radio-icon">💳</span> */}
                <span className="radio-content">
                  <span className="radio-title">Cashless Claim</span>
                  <span className="radio-desc">Payment directly to the hospital</span>
                </span>
              </label>
            </div>

            {/* Reimbursement Option */}
            <div className="radio-option">
              <input
                type="radio"
                id="reimbursement"
                name="claimType"
                value="reimbursement"
                checked={claimType === 'reimbursement'}
                onChange={(e) => setClaimType(e.target.value)}
              />
              <label htmlFor="reimbursement" className="radio-label">
                {/* <span className="radio-icon">💰</span> */}
                <span className="radio-content">
                  <span className="radio-title">Reimbursement Claim</span>
                  <span className="radio-desc">Payment to you after hospitalization</span>
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Accident Checkbox */}
        <div className="form-section">
          <label className="form-section-title">Additional Information</label>
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="isAccident"
              checked={isAccident}
              onChange={(e) => setIsAccident(e.target.checked)}
            />
            <label htmlFor="isAccident" className="checkbox-label">
              {/* <span className="checkbox-icon">⚠️</span> */}
              <span className="checkbox-content">
                <span className="checkbox-title">This was an accident</span>
                <span className="checkbox-desc">Check if this claim is related to an accident</span>
              </span>
            </label>
          </div>
          {isAccident && (
            <div className="alert alert-info">
              {/* <span className="alert-icon">ℹ️</span> */}
              <span className="alert-text">
                Accident claims will require additional verification and manual review. 
                You'll need to upload the FIR receipt as well.
              </span>
            </div>
          )}
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
