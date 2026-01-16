import PolicyCard from './PolicyCard';

export default function ActivePolicies({ policies = [] }) {
  return (
    <div className="bg-white rounded-3xl shadow-sm p-6 md:p-8">
      <h2 className="font-bold text-2xl md:text-3xl text-sureva-dark-blue mb-6" style={{ fontFamily: "'Outfit', sans-serif" }}>
        Your Active Policies
      </h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {policies.length > 0 ? (
          policies.map((policy, index) => {
            // Handle both old format (name, policyNumber, validity, status, id) and new format (policy_name, coverage_amount)
            const policyName = policy.name || policy.policy_name || 'Unknown Policy';
            const policyNumber = policy.policyNumber || `POL-${index + 1}`;
            const validity = policy.validity || 'Valid';
            const isActive = policy.status === 'active' || true; // Default to active since backend only returns active policies
            const isHealth = policyName.toLowerCase().includes('health');
            
            return (
              <PolicyCard
                key={policy.id || index}
                title={policyName}
                policyNumber={policyNumber}
                validity={validity}
                isActive={isActive}
                variant={isHealth ? 'green' : 'orange'}
              />
            );
          })
        ) : (
          <div style={{ 
            padding: '24px', 
            textAlign: 'center', 
            color: '#999999',
            fontFamily: "'Inter', sans-serif"
          }}>
            No active policies found
          </div>
        )}
      </div>
    </div>
  );
}
