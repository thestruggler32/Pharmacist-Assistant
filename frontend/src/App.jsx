import { Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Layout from './components/Layout';
import Upload from './pages/Upload';
import Review from './pages/Review';
import ApprovalQueue from './pages/ApprovalQueue';
import IssuePrescription from './pages/IssuePrescription';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Login />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="issue-prescription" element={<IssuePrescription />} />
        <Route path="review/:id" element={<Review />} />
        <Route path="approvals" element={<ApprovalQueue />} />
      </Route>
    </Routes>
  );
}
export default App;
