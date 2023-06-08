import ReactDOM from 'react-dom/client'
import MainWindow from './MainWindow'
import './main.css'
import {SetupUrlState} from '@figurl/interface'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  // <React.StrictMode>
  <SetupUrlState>
    <MainWindow />
  </SetupUrlState>
  // </React.StrictMode>,
)