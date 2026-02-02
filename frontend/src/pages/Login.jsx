import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { User, Stethoscope, Pill } from 'lucide-react';
import { motion } from 'framer-motion';
import { login } from '@/services/api';

const roles = [
    { id: 'patient1', label: 'John Doe', icon: User, color: 'text-blue-500', email: 'patient1@test.com' },
    { id: 'patient2', label: 'Jane Smith', icon: User, color: 'text-blue-400', email: 'patient2@test.com' },
    { id: 'patient3', label: 'Rajesh K.', icon: User, color: 'text-blue-300', email: 'patient3@test.com' },
    { id: 'doctor', label: 'Doctor', icon: Stethoscope, color: 'text-green-500', email: 'doctor@test.com' },
    { id: 'pharmacist', label: 'Pharmacist', icon: Pill, color: 'text-purple-500', email: 'pharmacist@test.com' },
];

export default function Login() {
    const [selectedRole, setSelectedRole] = useState('patient1');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async () => {
        setError('');
        setLoading(true);
        const roleData = roles.find(r => r.id === selectedRole);

        try {
            await login(roleData.email, 'password');
            navigate('/dashboard');
        } catch (err) {
            console.error(err);
            setError("Login Failed: " + (err.response?.data?.msg || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900 p-4">
            <div className="absolute top-4 right-4 text-xs text-gray-400">
                Demo: All passwords are "password"
            </div>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-2xl"
            >
                <Card className="border-t-4 border-t-primary shadow-xl">
                    <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold tracking-tight">Pharmacy App</CardTitle>
                        <CardDescription>Select your account to continue</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
                            {roles.map((role) => {
                                const Icon = role.icon;
                                const isSelected = selectedRole === role.id;
                                return (
                                    <div
                                        key={role.id}
                                        onClick={() => setSelectedRole(role.id)}
                                        className={`cursor-pointer flex flex-col items-center p-3 rounded-lg border-2 transition-all hover:bg-accent ${isSelected ? 'border-primary bg-accent' : 'border-transparent'
                                            }`}
                                    >
                                        <Icon className={`w-8 h-8 mb-2 ${role.color}`} />
                                        <span className="text-xs font-medium text-center">{role.label}</span>
                                    </div>
                                );
                            })}
                        </div>

                        {error && <p className="text-sm text-red-500 text-center">{error}</p>}

                    </CardContent>
                    <CardFooter>
                        <Button className="w-full" size="lg" onClick={handleLogin} disabled={loading}>
                            {loading ? 'Logging in...' : `Login as ${roles.find(r => r.id === selectedRole)?.label}`}
                        </Button>
                    </CardFooter>
                </Card>
            </motion.div>
        </div>
    );
}
