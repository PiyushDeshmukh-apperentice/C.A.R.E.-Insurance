import React, { useState } from 'react';
import '../styles/StepStyles.css';

/**
 * IncidentDetailsStep - Step 3
 * Enter incident details
 */
export default function IncidentDetailsStep({ formData, onNext, onPrevious }) {
  const [eventDate, setEventDate] = useState(formData.eventDate || '');
  const [eventTime, setEventTime] = useState(formData.eventTime || '');
  const [activity, setActivity] = useState(formData.activity || '');
  const [street, setStreet] = useState(formData.street || '');
  const [city, setCity] = useState(formData.city || '');
  const [state, setState] = useState(formData.state || '');
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!eventDate.trim()) {
      setError('Please enter the event date');
      return;
    }
    if (!eventTime.trim()) {
      setError('Please enter the event time');
      return;
    }
    if (!activity.trim()) {
      setError('Please select an activity type');
      return;
    }
    if (!street.trim()) {
      setError('Please enter the street name');
      return;
    }
    if (!city.trim()) {
      setError('Please enter the city');
      return;
    }
    if (!state.trim()) {
      setError('Please enter the state');
      return;
    }
    onNext({
      eventDate,
      eventTime,
      activity,
      street,
      city,
      state
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Incident Details</h2>
        <p className="step-description">
          Provide information about the incident
        </p>
      </div>

      <div className="step-content">
        {/* Event Date */}
        <div className="form-section">
          <label htmlFor="eventDate" className="form-section-title">Event Date</label>
          <input
            type="date"
            id="eventDate"
            className="policy-name-input"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
          />
          <p className="policy-help-text">
            Date when the incident occurred
          </p>
        </div>

        {/* Event Time */}
        <div className="form-section">
          <label htmlFor="eventTime" className="form-section-title">Event Time</label>
          <input
            type="time"
            id="eventTime"
            className="policy-name-input"
            value={eventTime}
            onChange={(e) => setEventTime(e.target.value)}
          />
          <p className="policy-help-text">
            Time when the incident occurred (24-hour format)
          </p>
        </div>

        {/* Activity Type */}
        <div className="form-section">
          <label htmlFor="activity" className="form-section-title">Type of Incident</label>
          <select
            id="activity"
            className="policy-name-input"
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
          >
            <option value="">Select incident type</option>
            <option value="road_accident">Road Accident</option>
            <option value="theft">Theft</option>
            <option value="vandalism">Vandalism</option>
            <option value="natural_calamity">Natural Calamity</option>
            <option value="third_party_damage">Third Party Damage</option>
            <option value="self_damage">Self Damage</option>
            <option value="fire">Fire</option>
          </select>
          <p className="policy-help-text">
            Select the type of incident
          </p>
        </div>

        {/* Location - Street */}
        <div className="form-section">
          <label htmlFor="street" className="form-section-title">Street Name</label>
          <input
            type="text"
            id="street"
            className="policy-name-input"
            placeholder="Enter street name"
            value={street}
            onChange={(e) => setStreet(e.target.value)}
          />
        </div>

        {/* Location - City */}
        <div className="form-section">
          <label htmlFor="city" className="form-section-title">City</label>
          <input
            type="text"
            id="city"
            className="policy-name-input"
            placeholder="Enter city name"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          />
        </div>

        {/* Location - State */}
        <div className="form-section">
          <label htmlFor="state" className="form-section-title">State</label>
          <input
            type="text"
            id="state"
            className="policy-name-input"
            placeholder="Enter state name"
            value={state}
            onChange={(e) => setState(e.target.value)}
          />
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
