import React from 'react';
import '../styles/StepStyles.css';
import '../styles/ReviewStyle.css';

/**
 * VehicleReviewStep - Step 6
 * Review all vehicle claim details before submission
 */
export default function VehicleReviewStep({
  formData,
  onNext,
  onPrevious,
  loading,
  error
}) {
  const vehicleTypes = {
    car: 'Four Wheeler (Car)',
    bike: 'Motorcycle/Bike',
    scooter: 'Scooter/Scooty',
    truck: 'Truck/Heavy Vehicle'
  };

  const activityTypes = {
    road_accident: 'Road Accident',
    theft: 'Theft',
    vandalism: 'Vandalism',
    natural_calamity: 'Natural Calamity',
    third_party_damage: 'Third Party Damage',
    self_damage: 'Self Damage',
    fire: 'Fire'
  };

  const genderDisplay = {
    male: 'Male',
    female: 'Female',
    other: 'Other'
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Review Your Claim</h2>
        <p className="step-description">
          Please review all information before submitting your vehicle insurance claim
        </p>
      </div>

      <div className="step-content">
        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            {/* <span className="alert-icon">❌</span> */}
            <span className="alert-text">{error}</span>
          </div>
        )}

        {/* Policy Details */}
        <div className="review-section">
          <h3 className="review-section-title">Policy Information</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Policy Name</span>
              <span className="review-value">{formData.policyName}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Vehicle Type</span>
              <span className="review-value">{vehicleTypes[formData.vehicleType]}</span>
            </div>
          </div>
        </div>

        {/* Vehicle Details */}
        <div className="review-section">
          <h3 className="review-section-title">Vehicle Information</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Vehicle Model</span>
              <span className="review-value">{formData.vehicleModel}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Registration Number</span>
              <span className="review-value">{formData.vehicleNumber}</span>
            </div>
          </div>
        </div>

        {/* Incident Details */}
        <div className="review-section">
          <h3 className="review-section-title">Incident Details</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Date</span>
              <span className="review-value">{formData.eventDate}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Time</span>
              <span className="review-value">{formData.eventTime}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Type</span>
              <span className="review-value">{activityTypes[formData.activity]}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Street</span>
              <span className="review-value">{formData.street}</span>
            </div>
            <div className="review-item">
              <span className="review-label">City</span>
              <span className="review-value">{formData.city}</span>
            </div>
            <div className="review-item">
              <span className="review-label">State</span>
              <span className="review-value">{formData.state}</span>
            </div>
          </div>
        </div>

        {/* Driver Details */}
        <div className="review-section">
          <h3 className="review-section-title">Driver Information</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Name</span>
              <span className="review-value">{formData.driverName}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Age</span>
              <span className="review-value">{formData.driverAge} years</span>
            </div>
            <div className="review-item">
              <span className="review-label">Gender</span>
              <span className="review-value">{genderDisplay[formData.driverGender]}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Licensed</span>
              <span className="review-value">
                {formData.licensed ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="review-item">
              <span className="review-label">Experience</span>
              <span className="review-value">⏳ {formData.experienceYears} years</span>
            </div>
            <div className="review-item">
              <span className="review-label">Under Influence</span>
              <span className="review-value">
                {formData.underInfluence ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>

        {/* Vehicle Image */}
        {formData.vehicleImage && (
          <div className="review-section">
            <h3 className="review-section-title">Vehicle Image</h3>
            <div style={{ textAlign: 'center', marginTop: '12px' }}>
              <img
                src={URL.createObjectURL(formData.vehicleImage)}
                alt="Vehicle preview"
                style={{
                  maxWidth: '100%',
                  maxHeight: '300px',
                  borderRadius: '10px',
                  border: '2px solid #DBF4FF',
                  objectFit: 'contain'
                }}
              />
              <p className="policy-help-text" style={{ marginTop: '12px' }}>
                {formData.vehicleImage.name}
              </p>
            </div>
          </div>
        )}

        {/* Confirmation Checkbox */}
        <div className="form-section">
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="confirm"
              defaultChecked
              disabled
            />
            <label htmlFor="confirm" className="checkbox-label">
              <span className="checkbox-content">
                I confirm that all information provided is accurate and complete
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Step Footer */}
      <div className="step-footer">
        <button
          className="btn btn-secondary"
          onClick={onPrevious}
          disabled={loading}
        >
          ← Previous
        </button>
        <button
          className={`btn btn-primary ${loading ? 'loading' : ''}`}
          onClick={onNext}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Submitting...
            </>
          ) : (
            <>
              Submit Claim
              <span className="btn-icon">✓</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
