import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { User, Stethoscope, Pill, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { login, verifyLicense } from '@/services/api';

const roles = [
    { id: 'patient', label: 'Patient', icon: User, color: 'text-blue-500', email: 'patient@test.com' },
    { id: 'doctor', label: 'Doctor', icon: Stethoscope, color: 'text-green-500', email: 'doctor@test.com' },
    { id: 'pharmacist', label: 'Pharmacist', icon: Pill, color: 'text-purple-500', email: 'pharmacist@test.com' },
];

export default function Login() {
    const [selectedRole, setSelectedRole] = useState('patient');
    const [license, setLicense] = useState('');
    const [isVerifying, setIsVerifying] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        setError('');
        const roleData = roles.find(r => r.id === selectedRole);

        try {
            if (selectedRole !== 'patient') {
                setIsVerifying(true);
                // Verify license (Mock API call)
                const verifyRes = await verifyLicense(license);
                if (!verifyRes.data.verified) {
                    setError("License Verification Failed");
                    setIsVerifying(false);
                    return;
                }
            }

            // Login
            // Note: For demo simplicity using hardcoded passwords from the plan's MOCK DB
            await login(roleData.email, 'password');
            navigate('/dashboard');

        } catch (err) {
            console.error(err);
            setError("Login Failed. Check console or credentials.");
        } finally {
            setIsVerifying(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900 p-4">
            <div className="absolute top-4 right-4 text-xs text-gray-400">
                Demo: pharmacist@test.com / password
            </div>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                <Card className="border-t-4 border-t-primary shadow-xl">
                    <CardHeader className="text-center">
                        <CardTitle className="text-3xl font-bold tracking-tight">Pharmacy App</CardTitle>
                        <CardDescription>Select your role to continue</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-3 gap-4">
                            {roles.map((role) => {
                                const Icon = role.icon;
                                const isSelected = selectedRole === role.id;
                                return (
                                    <div
                                        key={role.id}
                                        onClick={() => setSelectedRole(role.id)}
                                        className={`cursor-pointer flex flex-col items-center p-4 rounded-lg border-2 transition-all hover:bg-accent ${isSelected ? 'border-primary bg-accent' : 'border-transparent'
                                            }`}
                                    >
                                        <Icon className={`w-8 h-8 mb-2 ${role.color}`} />
                                        <span className="text-xs font-medium">{role.label}</span>
                                    </div>
                                );
                            })}
                        </div>

                        {selectedRole !== 'patient' && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="space-y-2 overflow-hidden"
                            >
                                <Label htmlFor="license">
                                    {selectedRole === 'doctor' ? 'Registration Number' : 'Drug License Number'}
                                </Label>
                                <div className="relative">
                                    <Input
                                        id="license"
                                        placeholder="Enter 'VALID' to pass verification"
                                        value={license}
                                        onChange={(e) => setLicense(e.target.value)}
                                    />
                                    {license.toUpperCase().startsWith('VALID') && (
                                        <CheckCircle className="absolute right-3 top-2.5 h-5 w-5 text-green-500" />
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Verification via {selectedRole === 'doctor' ? 'IDfy' : 'Surepass'} API (Mock)
                                </p>
                            </motion.div>
                        )}

                        {error && <p className="text-sm text-red-500 text-center">{error}</p>}

                    </CardContent>
                    <CardFooter>
                        <Button className="w-full" size="lg" onClick={handleLogin} disabled={isVerifying}>
                            {isVerifying ? 'Verifying License...' : `Login as ${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}`}
                        </Button>
                    </CardFooter>
                </Card>
            </motion.div>
        </div>
    );
}
