import Header from './components/Header';
import Footer from './components/Footer';
import MainContent from './components/MainContent';

function App() {
  return (
    // "w-full" ensures it takes full width
    // "min-h-screen" ensures it takes full height
    <div className="w-full min-h-screen flex flex-col font-sans text-gray-900 bg-gray-50">
      <Header />
      <MainContent />
      <Footer />
    </div>
  );
}

export default App;