import { Activity } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/login/Login';
import Loader from './components/Loader/Loader';
import Register from './components/register/Register';
import Dashboard from './components/dashboard/Dashboard';
import { useLoadingStore } from './store/useLoadingStore';
import './app.scss'
import { useWebSocket } from './hooks/useWebSocket';
import { useAuthInitializer } from './hooks/useAuthInitializer';

function App() {
  useAuthInitializer();
  useWebSocket();
  const isLoading = useLoadingStore((state) => state.isLoading);

  return (
    <div className='app'>  
      <BrowserRouter>
        <Routes>
          <Route path="login" element={<Login />}/>
          <Route path='register' element={<Register />}/>
          <Route path='dashboard' element={<Dashboard />}/>
          <Route path="*" element={<Login />} />
        </Routes>
      </BrowserRouter>
      <Activity mode={isLoading ? 'visible' : 'hidden'}>
        <Loader />
      </Activity>
      <Toaster />
    </div>
  )
}

export default App
