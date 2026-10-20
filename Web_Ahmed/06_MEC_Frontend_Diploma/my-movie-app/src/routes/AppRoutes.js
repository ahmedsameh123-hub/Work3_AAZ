import React from 'react';
import { Routes, Route } from 'react-router-dom'; // تأكد من استيراد Routes و Route
import HomePage from '../pages/HomePage';
import MovieDetails from '../pages/MovieDetails';
import Login from '../pages/Login';
import Signup from '../pages/Signup';
import NotFound from '../pages/NotFound';
import PrivateRoute from '../components/PrivateRoute';

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/movies/:id" element={<PrivateRoute><MovieDetails /></PrivateRoute>} />
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<Signup />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;
