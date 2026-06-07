import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/login/Login';
import Register from './components/register/Register';

function App() {
  return (
    <>  
      <BrowserRouter>
        <Routes>
          <Route path="login" element={<Login />}/>
          <Route path='register' element={<Register />}/>
        </Routes>
      </BrowserRouter>
      <Toaster />
    </>
  )
}

export default App
