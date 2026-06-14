import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/login/Login';
import Register from './components/register/Register';
import Dashboard from './components/dashboard/Dashboard';
import './app.scss'

function App() {
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
      <Toaster />
    </div>
  )
}

export default App
