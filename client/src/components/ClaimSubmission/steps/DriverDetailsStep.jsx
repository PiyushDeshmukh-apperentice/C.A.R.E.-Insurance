import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * DriverDetailsStep - Step 4
 * Enter driver details
 */
export default function DriverDetailsStep({ formData, onNext, onPrevious }) {
  const [driverName, setDriverName] = useState(formData.driverName || '');
  const [driverAge, setDriverAge] = useState(formData.driverAge || '');
  const [driverGender, setDriverGender] = useState(formData.driverGender || '');
  const [licensed, setLicensed] = useState(formData.licensed || false);
  const [experienceYears, setExperienceYears] = useState(formData.experienceYears || '');
  const [underInfluence, setUnderInfluence] = useState(formData.underInfluence || false);
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!driverName.trim()) {
      setError('Please enter driver name');
      return;
    }
    if (!driverAge || driverAge < 18 || driverAge > 120) {
      setError('Please enter a valid driver age (18-120)');
      return;
    }
    if (!driverGender) {
      setError('Please select driver gender');
      return;
    }
    if (experienceYears === '' || experienceYears < 0 || experienceYears > 80) {
      setError('Please enter valid driving experience (0-80 years)');
      return;
    }
    onNext({
      driverName,
      driverAge,
      driverGender,
      licensed,
      experienceYears,
      underInfluence
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Driver Details</h2>
        <p className="step-description">
          Provide information about the driver
        </p>
      </div>

      <div className="step-content">
        {/* Driver Name */}
        <div className="form-section">
          <label htmlFor="driverName" className="form-section-title">Driver Name</label>
          <input
            type="text"
            id="driverName"
            className="policy-name-input"
            placeholder="Enter driver's full name"
            value={driverName}
            onChange={(e) => setDriverName(e.target.value)}
          />
        </div>

        {/* Driver Age */}
        <div className="form-section">
          <label htmlFor="driverAge" className="form-section-title">Driver Age</label>
          <input
            type="number"
            id="driverAge"
            className="policy-name-input"
            placeholder="Enter driver's age"
            min="18"
            max="120"
            value={driverAge}
            onChange={(e) => setDriverAge(e.target.value)}
          />
        </div>

        {/* Driver Gender */}
        <div className="form-section">
          <label htmlFor="driverGender" className="form-section-title">Driver Gender</label>
          <select
            id="driverGender"
            className="policy-name-input"
            value={driverGender}
            onChange={(e) => setDriverGender(e.target.value)}
          >
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Licensed */}
        <div className="form-section">
          <label className="form-section-title">Driving License</label>
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="licensed"
              checked={licensed}
              onChange={(e) => setLicensed(e.target.checked)}
            />
            <label htmlFor="licensed" className="checkbox-label">
              <span className="checkbox-icon">✓</span>
              <span className="checkbox-content">
                <span className="checkbox-title">Driver has a valid driving license</span>
              </span>
            </label>
          </div>
        </div>

        {/* Experience Years */}
        <div className="form-section">
          <label htmlFor="experienceYears" className="form-section-title">Driving Experience (Years)</label>
          <input
            type="number"
            id="experienceYears"
            className="policy-name-input"
            placeholder="Years of driving experience"
            min="0"
            max="80"
            value={experienceYears}
            onChange={(e) => setExperienceYears(e.target.value)}
          />
        </div>

        {/* Under Influence */}
        <div className="form-section">
          <label className="form-section-title">Important</label>
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="underInfluence"
              checked={underInfluence}
              onChange={(e) => setUnderInfluence(e.target.checked)}
            />
            <label htmlFor="underInfluence" className="checkbox-label">
              {/* <span className="checkbox-icon">🚫</span> */}
              <span className="checkbox-content">
                <span className="checkbox-title">Driver was under the influence of alcohol/drugs</span>
              </span>
            </label>
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
