import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Tabla from './PaginasWeb/Tabla';


function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path='/' element={<Tabla/>}/>



      </Routes>
    </BrowserRouter>



  );
}

export default App;
