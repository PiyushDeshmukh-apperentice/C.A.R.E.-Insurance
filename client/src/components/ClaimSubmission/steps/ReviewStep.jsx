import React from 'react';
import '../styles/StepStyles.css';
import '../styles/ReviewStyle.css';

/**
 * ReviewStep - Step 3
 * Review claim details before submission
 */
export default function ReviewStep({
  formData,
  onNext,
  onPrevious,
  loading,
  error
}) {
  const documents = formData.documents || {};
  const docCount = Object.keys(documents).length;

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Review Your Claim</h2>
        <p className="step-description">
          Please review all information before submitting your claim
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

        {/* Claim Type Summary */}
        <div className="review-section">
          <h3 className="review-section-title">Claim Details</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Claim Type</span>
              <span className="review-value">
                {formData.claimType === 'cashless' ? 'Cashless Claim' : 'Reimbursement Claim'}
              </span>
            </div>
            <div className="review-item">
              <span className="review-label">Policy Name</span>
              <span className="review-value">
                {formData.policyName || 'Not specified'}
              </span>
            </div>
            {formData.isAccident && (
              <div className="review-item">
                <span className="review-label">Accident Claim</span>
                <span className="review-value alert-warning-badge">
                  Requires Manual Review
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Documents Summary */}
        <div className="review-section">
          <h3 className="review-section-title">Documents Uploaded</h3>
          <div className="documents-summary">
            <p className="summary-text">
              Total documents: <strong>{docCount}</strong>
            </p>
            <div className="documents-list">
              {Object.entries(documents).map(([key, file]) => (
                <div key={key} className="document-summary-item">
                  <span className="doc-check">✓</span>
                  <span className="doc-name">
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span className="doc-size">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Submission Info */}
        <div className="review-section">
          <h3 className="review-section-title">Submission Information</h3>
          {formData.isAccident ? (
            <div className="alert alert-info">
              {/* <span className="alert-icon">ℹ️</span> */}
              <div className="alert-content">
                <p className="alert-title">Accident Claim Processing</p>
                <p className="alert-text">
                  Your claim will be processed on the frontend and marked for manual review.
                  You will receive an audit reference ID for tracking.
                </p>
              </div>
            </div>
          ) : (
            <div className="alert alert-info">
              {/* <span className="alert-icon">ℹ️</span> */}
              <div className="alert-content">
                <p className="alert-title">Automatic Processing</p>
                <p className="alert-text">
                  Your claim will be automatically processed by our health claim engine.
                  You'll receive the decision immediately.
                </p>
              </div>
            </div>
          )}
        </div>

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
