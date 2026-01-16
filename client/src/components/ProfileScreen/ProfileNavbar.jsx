import React, { useState } from 'react';
import { LogOut } from 'lucide-react';

export default function ProfileNavbar() {
  const [isHovered, setIsHovered] = useState(false);

  const handleLogout = () => {
    // Handle logout logic here
    console.log('Logged out');
    // Navigate to home or login page
    window.location.href = '/';
  };

  return (
    <header className="py-6" style={{background: 'var(--bg-highlight)'}}>
      <div className="max-w-[1320px] mx-auto px-4">
        {/* Navbar Container */}
        <div className="bg-white rounded-[20px] shadow-sm px-6 lg:px-10">
          <div className="flex justify-between items-center h-[72px]">
            
            {/* Logo */}
            <div className="flex items-center gap-3">
              <img
                src="/images/img_68b9b823a50348f.png"
                alt="Sureva Logo"
                className="w-[96px] h-auto"
              />
            </div>

            {/* Logout Button */}
            <button
              className="text-lg font-semibold leading-5 text-white rounded-[14px] py-3 px-6 flex items-center gap-2"
              onClick={handleLogout}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              style={{ 
                backgroundColor: 'var(--primary-background)',
                cursor: 'pointer',
                transition: 'all 0.3s ease-in-out',
                transform: isHovered ? 'scale(1.05)' : 'scale(1)',
                boxShadow: isHovered ? '0 4px 12px rgba(0, 0, 0, 0.15)' : '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}
            >
              <LogOut 
                size={18}
                style={{
                  transform: isHovered ? 'translateX(-4px)' : 'translateX(0)',
                  transition: 'transform 0.3s'
                }}
              />
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
