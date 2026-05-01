import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Tabla from './PaginasWeb/Tabla';
import Tabla2 from './PaginasWeb/Tabla2';

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path='/' element={<Tabla/>}/>
        <Route path='/hola' element={<Tabla2/>}/>



      </Routes>
    </BrowserRouter>



  );
}

export default App;
