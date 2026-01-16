import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * ImageUploadStep - Step 5
 * Upload vehicle image
 */
export default function ImageUploadStep({ formData, onNext, onPrevious }) {
  const [vehicleImage, setVehicleImage] = useState(formData.vehicleImage || null);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = React.useRef(null);

  const handleFileSelect = (file) => {
    if (file) {
      // Validate file type (must be image)
      if (!file.type.includes('image')) {
        setError('Please upload an image file (JPG, PNG, etc.)');
        setTimeout(() => setError(''), 5000);
        return;
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        setError('Image size must be less than 10MB');
        setTimeout(() => setError(''), 5000);
        return;
      }

      setVehicleImage(file);
      setUploadProgress(100);
    }
  };

  const handleNext = () => {
    if (!vehicleImage) {
      setError('Please upload a vehicle image');
      return;
    }
    onNext({
      vehicleImage
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Vehicle Image</h2>
        <p className="step-description">
          Upload a clear image of your vehicle showing the damage
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

        {/* Image Upload Section */}
        <div className="form-section">
          <label className="form-section-title">Vehicle Image</label>
          {vehicleImage ? (
            <div className="image-uploaded">
              <div className="image-preview">
                <img
                  src={URL.createObjectURL(vehicleImage)}
                  alt="Vehicle preview"
                  style={{
                    maxWidth: '100%',
                    maxHeight: '300px',
                    borderRadius: '10px',
                    objectFit: 'contain'
                  }}
                />
              </div>
              <div className="image-details">
                <p className="uploaded-filename">{vehicleImage.name}</p>
                <p className="uploaded-size">{(vehicleImage.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button
                className="btn-replace"
                onClick={() => fileInputRef.current?.click()}
              >
                Replace Image
              </button>
            </div>
          ) : (
            <div
              className="document-upload-area"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files[0]) {
                  handleFileSelect(e.dataTransfer.files[0]);
                }
              }}
            >
              {/* <span className="upload-icon">📸</span> */}
              <p className="upload-text">Click or drag to upload vehicle image</p>
              <p className="upload-hint">Max 10MB (JPG, PNG, etc.)</p>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => handleFileSelect(e.target.files?.[0])}
          />

          <p className="policy-help-text" style={{ marginTop: '16px' }}>
            Upload a clear photo of your vehicle. Show the damage clearly for better claim processing.
          </p>
        </div>

        {/* Info Alert */}
        <div className="alert alert-info">
          {/* <span className="alert-icon">ℹ️</span> */}
          <div className="alert-content">
            <p className="alert-title">Best Practices:</p>
            <p className="alert-text">
              • Capture vehicle from multiple angles if damage is visible<br/>
              • Ensure good lighting<br/>
              • Include registration plate in at least one image<br/>
              • Avoid blurry or tilted images
            </p>
          </div>
        </div>
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
