import Routes from './Routes';
import { ToastProvider } from './components/Toast';

function App() {
  return (
    <ToastProvider>
      <Routes />
    </ToastProvider>
  );
}

export default App;