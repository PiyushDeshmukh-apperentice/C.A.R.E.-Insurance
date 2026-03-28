import React, { useState } from 'react';
import '../styles/StepStyles.css';
import '../styles/SuccessStyle.css';

/**
 * SuccessStep - Final Step
 * Display claim submission result and next steps
 * Supports both Health and Vehicle Insurance claims
 */
export default function SuccessStep({ claimResult, isAccident, claimType, onClose }) {
  const [showDetails, setShowDetails] = useState(false);
  const [showDamageAnalysis, setShowDamageAnalysis] = useState(false);

  if (!claimResult) {
    return (
      <div className="step-container">
        <div className="success-loading">
          <span className="spinner"></span>
          <p>Processing your claim...</p>
        </div>
      </div>
    );
  }

  const isVehicle = claimType === 'vehicle';
  const isApproved = claimResult.decision === 'APPROVED';
  const isPending = claimResult.decision === 'PENDING_REVIEW' || claimResult.decision === 'FAILED';

  // Vehicle-specific UI
  if (isVehicle) {
    const hasOutputImage = claimResult.output_image_url;
    const damageAnalysis = claimResult.damage_analysis;

    return (
      <div className="step-container vehicle-success-container">
        {/* Vehicle Success Header */}
        <div className="vehicle-success-header">
          <div className={`vehicle-success-icon ${isApproved ? 'approved' : isPending ? 'pending' : 'rejected'}`}>
            {isApproved ? '🎉' : isPending ? '⏳' : '⚠️'}
          </div>
          <h2 className="vehicle-success-title">
            {isApproved
              ? 'Claim Verified'
              : isPending
                ? 'Claim Under Review'
                : 'Claim Submitted'}
          </h2>
          <p className="vehicle-success-subtitle">
            {isApproved
              ? 'Your vehicle insurance claim is under review and has been verified by our system'
              : isPending
                ? 'Our team is reviewing your vehicle claim'
                : 'Your claim has been successfully submitted'}
          </p>
        </div>

        {/* Main Content */}
        <div className="vehicle-success-content">
          {/* Claim Status - PROMINENT */}
          <div className="vehicle-status-alert">
            <div className={`status-badge ${isApproved ? 'approved' : isPending ? 'pending' : 'submitted'}`}>
              {isApproved ? '✅ CLAIM VERIFIED' : isPending ? '⏳ UNDER REVIEW' : '📋 CLAIM SUBMITTED'}
            </div>
          </div>

          {/* Output Image Section */}
          {hasOutputImage && (
            <div className="vehicle-image-section">
              <h3 className="section-title">🖼️ Damage Assessment</h3>
              <div className="vehicle-image-container">
                <img
                  src={`http://localhost:8000${claimResult.output_image_url}`}
                  alt="Vehicle damage assessment"
                  className="vehicle-output-image"
                  onError={(e) => {
                    console.error('❌ Image load error:', `http://localhost:8000${claimResult.output_image_url}`);
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML += '<p style="text-align:center; color:#999; padding:20px;">Image could not be loaded</p>';
                  }}
                  onLoad={() => {
                    console.log('✅ Image loaded successfully:', `http://localhost:8000${claimResult.output_image_url}`);
                  }}
                />
              </div>
            </div>
          )}

          {/* Claim ID Section */}
          <div className="vehicle-info-section">
            <div className="vehicle-info-grid">
              <div className="vehicle-info-item">
                <span className="vehicle-info-label">📋 Claim ID</span>
                <code className="vehicle-info-value">{claimResult.claim_id}</code>
                <button
                  className="vehicle-copy-btn"
                  onClick={() => {
                    navigator.clipboard.writeText(claimResult.claim_id);
                    alert('Claim ID copied to clipboard!');
                  }}
                  title="Copy to clipboard"
                >
                  📋
                </button>
              </div>
              <div className="vehicle-info-item">
                <span className="vehicle-info-label">📍 Reference</span>
                <code className="vehicle-info-value">{claimResult.audit_reference_id}</code>
              </div>
            </div>
          </div>

          {/* Decision Card - Attractive Design without numbers */}
          <div className="vehicle-decision-section">
            <h3 className="section-title">📊 Claim Decision</h3>
            <div className={`vehicle-decision-card decision-${claimResult.decision.toLowerCase()}`}>
              <div className="vehicle-decision-icon">
                {isApproved ? '✅' : isPending ? '⏳' : '⚠️'}
              </div>
              <div className="vehicle-decision-content">
                <h4 className="vehicle-decision-status">{isApproved ? 'VERIFIED' : isPending ? 'UNDER REVIEW' : 'REJECTED'}</h4>
                <p className="vehicle-decision-summary">{claimResult.summary}</p>
              </div>
            </div>
          </div>

          {/* Estimated Cost Section */}
          {claimResult.estimated_cost > 0 && (
            <div className="vehicle-cost-section">
              <h3 className="section-title">💰 Estimated Cost</h3>
              <div className="vehicle-cost-display">
                <span className="vehicle-cost-currency">₹</span>
                <span className="vehicle-cost-amount">{claimResult.estimated_cost.toLocaleString('en-IN')}</span>
              </div>
              {claimResult.cost_breakdown && claimResult.cost_breakdown.length > 0 && (
                <div className="vehicle-cost-breakdown">
                  {claimResult.cost_breakdown && claimResult.cost_breakdown.length > 0 && (
                    <div className="vehicle-cost-breakdown">
                      {claimResult.cost_breakdown.map((item, idx) => {
                        // Grab the part name, prioritizing the AI's actual keys
                        const partName = item.part_name || item.part || item.category || item.name || `Item ${idx + 1}`;

                        // Grab the cost, prioritizing the AI's actual keys
                        const itemCost = item.estimated_cost || item.cost || item.amount || 0;

                        return (
                          <div key={idx} className="cost-item">
                            <span className="cost-label">{partName}</span>
                            <span className="cost-value">₹ {Number(itemCost).toLocaleString('en-IN')}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Damage Analysis Section - HIDDEN */}
          {/* Commented out as per requirement */}
        </div>

        {/* Next Steps */}
        <div className="vehicle-next-steps">
          <h3 className="section-title">📝 What's Next?</h3>
          <div className="vehicle-steps-list">
            {isApproved ? (
              <>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">1</span>
                  <p className="vehicle-step-text">Claim approved and registered in our system</p>
                </div>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">2</span>
                  <p className="vehicle-step-text">Settlement amount will be processed to your account</p>
                </div>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">3</span>
                  <p className="vehicle-step-text">You'll receive a confirmation email with details</p>
                </div>
              </>
            ) : (
              <>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">1</span>
                  <p className="vehicle-step-text">Our team is reviewing your claim details</p>
                </div>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">2</span>
                  <p className="vehicle-step-text">You may be contacted for additional information</p>
                </div>
                <div className="vehicle-step-item">
                  <span className="vehicle-step-icon">3</span>
                  <p className="vehicle-step-text">Decision will be notified within 5 business days</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="vehicle-success-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Back to Profile
          </button>
          <button className="btn btn-primary">
            Track Status →
          </button>
        </div>
      </div>
    );
  }

  // Health Insurance UI (original)
  return (
    <div className="step-container">
      {/* Success Header */}
      <div className="success-header">
        <div className={`success-icon ${isApproved ? 'approved' : isPending ? 'pending' : 'rejected'}`}>
          {isApproved ? '✓' : isPending ? '⏳' : '✕'}
        </div>
        <h2 className="success-title">
          {isApproved
            ? 'Claim Approved!'
            : isPending
              ? 'Claim Submitted for Review'
              : 'Claim Requires Review'}
        </h2>
        <p className="success-subtitle">
          {isApproved
            ? 'Your claim has been approved successfully'
            : isPending
              ? 'Your claim has been submitted and will be reviewed'
              : 'Your claim needs additional review'}
        </p>
      </div>

      {/* Main Content */}
      <div className="success-content">
        {/* Acknowledgement Message */}
        {claimResult.acknowledgement && (
          <div className="success-section">
            <div className="alert alert-success">
              {/* <span className="alert-icon">✅</span> */}
              <div className="alert-content">
                <p className="alert-text">{claimResult.acknowledgement}</p>
              </div>
            </div>
          </div>
        )}

        {/* Claim ID and Reference */}
        <div className="success-section info-section">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Claim ID</span>
              <code className="info-val vehicle insurance claim has been successfully received and registered. We will process your claim and notify you with the decision shortly.ue">{claimResult.claim_id}</code>
              <button
                className="copy-btn"
                onClick={() => {
                  navigator.clipboard.writeText(claimResult.claim_id);
                  alert('Claim ID copied!');
                }}
              >
                Copy
              </button>
            </div>
            <div className="info-item">
              <span className="info-label">Audit Reference</span>
              <code className="info-value">{claimResult.audit_reference_id}</code>
            </div>
          </div>
        </div>

        {/* Decision Summary */}
        <div className="success-section decision-section">
          <h3 className="section-title">Claim Decision</h3>
          <div className={`decision-card ${claimResult.decision.toLowerCase()}`}>
            <div className="decision-header">
              <span className="decision-badge">{claimResult.decision}</span>
              {claimResult.confidence && (
                <span className="confidence-badge">
                  Confidence: {(claimResult.confidence * 100).toFixed(1)}%
                </span>
              )}
            </div>
            <p className="decision-summary">{claimResult.summary}</p>
          </div>
        </div>

        {/* Accident Notice */}
        {isAccident && (
          <div className="success-section">
            <div className="alert alert-warning">
              {/* <span className="alert-icon">⚠️</span> */}
              <div className="alert-content">
                <p className="alert-title">Accident Claim - Manual Review Required</p>
                <p className="alert-text">
                  Your claim has been marked for manual review because it's related to an accident.
                  Our team will contact you within 24 hours with more information.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Detailed Results */}
        {showDetails && (
          <div className="success-section details-section">
            <h3 className="section-title">Detailed Analysis</h3>

            {claimResult.diagnosis && (
              <div className="detail-item">
                <span className="detail-label">Diagnosis</span>
                <p className="detail-value">{claimResult.diagnosis}</p>
              </div>
            )}

            {claimResult.decision_reasons && claimResult.decision_reasons.length > 0 && (
              <div className="detail-item">
                <span className="detail-label">Decision Reasons</span>
                <ul className="detail-list">
                  {claimResult.decision_reasons.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            {claimResult.applied_clauses && claimResult.applied_clauses.length > 0 && (
              <div className="detail-item">
                <span className="detail-label">Applied Clauses</span>
                <ul className="detail-list">
                  {claimResult.applied_clauses.map((clause, idx) => (
                    <li key={idx}>{clause}</li>
                  ))}
                </ul>
              </div>
            )}

            {claimResult.ignored_exclusions && claimResult.ignored_exclusions.length > 0 && (
              <div className="detail-item">
                <span className="detail-label">Ignored Exclusions</span>
                <ul className="detail-list">
                  {claimResult.ignored_exclusions.map((exclusion, idx) => (
                    <li key={idx}>{exclusion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Show Details Toggle */}
        {(claimResult.diagnosis ||
          claimResult.decision_reasons?.length > 0 ||
          claimResult.applied_clauses?.length > 0 ||
          claimResult.ignored_exclusions?.length > 0) && (
            <button
              className="btn-toggle-details"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? '← Hide Details' : 'Show Details →'}
            </button>
          )}
      </div>

      {/* Next Steps */}
      <div className="success-section next-steps">
        <h3 className="section-title">What's Next?</h3>
        <div className="steps-list">
          {isAccident ? (
            <>
              <div className="step-item">
                <span className="step-number">1</span>
                <p className="step-text">Our team will review your accident claim</p>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <p className="step-text">You'll receive a call within 24 hours</p>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <p className="step-text">Additional documents may be requested</p>
              </div>
            </>
          ) : isApproved ? (
            <>
              <div className="step-item">
                <span className="step-number">1</span>
                <p className="step-text">Your claim has been approved</p>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <p className="step-text">
                  {claimResult.decision === 'CASHLESS'
                    ? 'Payment will be made directly to the hospital'
                    : 'Reimbursement will be processed to your account'}
                </p>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <p className="step-text">Check your email for payment confirmation</p>
              </div>
            </>
          ) : (
            <>
              <div className="step-item">
                <span className="step-number">1</span>
                <p className="step-text">Your claim is under review</p>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <p className="step-text">You can track its status in your dashboard</p>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <p className="step-text">We'll notify you once the review is complete</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="success-footer">
        <button className="btn btn-secondary" onClick={onClose}>
          Close
        </button>
        <button className="btn btn-primary">
          View Claim Status →
        </button>
      </div>
    </div>
  );
}
