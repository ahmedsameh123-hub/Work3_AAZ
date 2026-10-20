import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // استخدام useState لتخزين حالة المستخدم

  const login = (userData) => {
    setUser(userData); // تسجيل الدخول وتحديث حالة المستخدم
  };

  const logout = () => {
    setUser(null); // تسجيل الخروج
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// تصدير الدالة useAuth
export const useAuth = () => {
  return useContext(AuthContext); // استخدام useContext للوصول إلى السياق
};
