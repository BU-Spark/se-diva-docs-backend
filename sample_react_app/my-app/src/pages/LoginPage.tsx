import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await axios.post('https://your-authentication-api/login', {
        username,
        password,
      });

      if (response.status === 200) {
        // Assuming the token is in the response data
        localStorage.setItem('token', response.data.token);
        navigate('/important-contacts');
      } else {
        setError('Invalid username or password');
      }
    } catch (error) {
      setError('Invalid username or password');
    }
  };

  return (
    // ... (rest of the component)
  );
};

export default LoginPage;
