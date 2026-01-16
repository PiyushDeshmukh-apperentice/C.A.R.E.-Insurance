import React from 'react';
import './ClaimTypeSelector.css';

/**
 * ClaimTypeSelector Modal
 * Allows user to select between Health Insurance Claim or Vehicle Insurance Claim
 */
export default function ClaimTypeSelector({ isOpen, onClose, onSelect }) {
  if (!isOpen) return null;

  return (
    <div className="claim-modal-overlay">
      <div className="claim-modal-container">
        {/* Modal Header */}
        <div className="claim-modal-header">
          <h2 className="claim-modal-title">Submit Insurance Claim</h2>
          <button
            className="claim-modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="claim-modal-body">
          <p className="claim-modal-description">
            Select the type of insurance claim you want to submit:
          </p>

          <div className="claim-options-container">
            {/* Health Insurance Claim Option */}
            <button
              className="claim-option-card health-card"
              onClick={() => onSelect('health')}
            >
              <div className="claim-option-icon">🏥</div>
              <h3 className="claim-option-title">Health Insurance Claim</h3>
              <p className="claim-option-description">
                Submit medical claims for hospitalization, treatment, and medical expenses
              </p>
            </button>

            {/* Vehicle Insurance Claim Option */}
            <button
              className="claim-option-card vehicle-card"
              onClick={() => onSelect('vehicle')}
            >
              <div className="claim-option-icon">🚗</div>
              <h3 className="claim-option-title">Vehicle Insurance Claim</h3>
              <p className="claim-option-description">
                Submit claims for vehicle damage, accidents, and related incidents
              </p>
            </button>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="claim-modal-footer">
          <button
            className="claim-modal-btn-cancel"
            onClick={onClose}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
