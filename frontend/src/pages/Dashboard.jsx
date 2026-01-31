import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, FileText, User, Activity, History } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { logout } from '@/services/api';

export default function Dashboard() {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    const { t } = useTranslation();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        } else {
            // navigate('/'); 
            // For fallback/dev allow viewing without login if needed, or redirect
        }
    }, []);

    if (!user) return <div className="p-8">Loading...</div>;

    return (
        <div className="container py-8 max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('welcome')}, {user.name}</h1>
                    <p className="text-muted-foreground capitalize">Role: {user.role}</p>
                </div>
                <Button variant="outline" onClick={logout}>Logout</Button>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Pharmacist Actions */}
                {user.role === 'pharmacist' && (
                    <Card className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/upload')}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">New Scan</CardTitle>
                            <Upload className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">Upload Prescription</div>
                            <p className="text-xs text-muted-foreground">Detailed OCR analysis</p>
                        </CardContent>
                    </Card>
                )}

                {/* Doctor Actions */}
                {user.role === 'doctor' && (
                    <>
                        <Card className="border-l-4 border-l-green-500">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Patients</CardTitle>
                                <User className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">View History</div>
                            </CardContent>
                        </Card>
                        <Card className="border-l-4 border-l-green-500">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Prescribe</CardTitle>
                                <FileText className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">New Rx</div>
                            </CardContent>
                        </Card>
                    </>
                )}

                {/* Common Stats */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">+12</div>
                        <p className="text-xs text-muted-foreground">Prescriptions processed this week</p>
                    </CardContent>
                </Card>
            </div>

            <div className="mt-8">
                <h2 className="text-xl font-semibold mb-4">Recent Prescriptions</h2>
                <Card>
                    <div className="p-4 text-center text-muted-foreground">
                        No recent prescriptions found.
                    </div>
                </Card>
            </div>
        </div>
    );
}
