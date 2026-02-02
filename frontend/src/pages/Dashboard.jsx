import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, Eye, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { logout } from '@/services/api';
import axios from 'axios';

export default function Dashboard() {
    const [user, setUser] = useState(null);
    const [prescriptions, setPrescriptions] = useState([]);
    const [filter, setFilter] = useState('all');
    const navigate = useNavigate();
    const { t } = useTranslation();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }

        const fetchPrescriptions = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('/api/prescriptions', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setPrescriptions(response.data.prescriptions || []);
            } catch (error) {
                console.error('Failed to fetch prescriptions:', error);
            }
        };

        fetchPrescriptions();
    }, []);

    if (!user) return <div className="p-8">Loading...</div>;

    const statusColors = {
        'pending': 'bg-yellow-500',
        'approved': 'bg-green-500',
        'rejected': 'bg-red-500'
    };

    const filteredPrescriptions = prescriptions.filter(p =>
        filter === 'all' || p.status === filter
    );

    return (
        <div className="container py-8 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('welcome')}, {user.name}</h1>
                    <p className="text-muted-foreground capitalize">Role: {user.role}</p>
                </div>
                <div className="flex gap-2">
                    <Button onClick={() => navigate('/upload')} className="bg-purple-600 hover:bg-purple-700">
                        <Upload className="h-4 w-4 mr-2" />
                        New Scan
                    </Button>
                    <Button variant="outline" onClick={logout}>
                        <LogOut className="h-4 w-4 mr-2" />
                        Logout
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3 mb-8">
                <Card className="border-l-4 border-l-yellow-500">
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                            {prescriptions.filter(p => p.status === 'pending').length}
                        </div>
                        <p className="text-sm text-gray-600">Pending Review</p>
                    </CardContent>
                </Card>
                <Card className="border-l-4 border-l-green-500">
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                            {prescriptions.filter(p => p.status === 'approved').length}
                        </div>
                        <p className="text-sm text-gray-600">Approved</p>
                    </CardContent>
                </Card>
                <Card className="border-l-4 border-l-blue-500">
                    <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                            {prescriptions.length}
                        </div>
                        <p className="text-sm text-gray-600">Total Prescriptions</p>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>All Prescriptions</CardTitle>
                        <div className="flex gap-2">
                            <Button
                                variant={filter === 'all' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setFilter('all')}
                            >
                                All
                            </Button>
                            <Button
                                variant={filter === 'pending' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setFilter('pending')}
                            >
                                Pending
                            </Button>
                            <Button
                                variant={filter === 'approved' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setFilter('approved')}
                            >
                                Approved
                            </Button>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {filteredPrescriptions.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <p className="text-lg font-medium mb-2">No prescriptions found</p>
                            <p className="text-sm mb-4">Upload your first prescription to get started</p>
                            <Button onClick={() => user.role === 'doctor' ? navigate('/issue-prescription') : navigate('/upload')}>
                                <Upload className="h-4 w-4 mr-2" />
                                {user.role === 'doctor' ? 'Issue Prescription' : 'Upload Prescription'}
                            </Button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50">
                                    <tr className="border-b">
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Uploaded By</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Medicines</th>
                                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredPrescriptions.map((prescription) => (
                                        <tr key={prescription.id} className="border-b hover:bg-gray-50 transition-colors">
                                            <td className="px-4 py-3 text-sm">
                                                {new Date(prescription.timestamp).toLocaleDateString()}
                                            </td>
                                            <td className="px-4 py-3 text-sm">{prescription.uploaded_by}</td>
                                            <td className="px-4 py-3 text-sm">
                                                {prescription.medicines?.length || 0} item(s)
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge className={statusColors[prescription.status]}>
                                                    {prescription.status.toUpperCase()}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => navigate(`/review/${prescription.id}`)}
                                                >
                                                    <Eye className="h-4 w-4 mr-1" />
                                                    {user.role === 'pharmacist' && prescription.status === 'pending' ? 'Review' : 'View'}
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}


