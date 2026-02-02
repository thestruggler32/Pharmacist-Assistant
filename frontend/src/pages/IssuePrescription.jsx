import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Trash2, Plus } from 'lucide-react';

export default function IssuePrescription() {
    const navigate = useNavigate();
    const [patientEmail, setPatientEmail] = useState('');
    const [notes, setNotes] = useState('');
    const [medicines, setMedicines] = useState([
        { name: '', dosage: '', duration: '', instructions: '' }
    ]);
    const [loading, setLoading] = useState(false);

    const handleAddMedicine = () => {
        setMedicines([...medicines, { name: '', dosage: '', duration: '', instructions: '' }]);
    };

    const handleRemoveMedicine = (index) => {
        setMedicines(medicines.filter((_, i) => i !== index));
    };

    const handleMedicineChange = (index, field, value) => {
        const updated = [...medicines];
        updated[index][field] = value;
        setMedicines(updated);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('/api/prescriptions/issue', {
                patient_email: patientEmail,
                medicines: medicines.filter(m => m.name), // Remove empty entries
                notes: notes
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            alert('Prescription issued successfully!');
            navigate('/dashboard');
        } catch (error) {
            alert(`Failed to issue prescription: ${error.response?.data?.msg || error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6">Issue Digital Prescription</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Patient Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <Label htmlFor="patientEmail">Patient Email *</Label>
                            <Input
                                id="patientEmail"
                                type="email"
                                value={patientEmail}
                                onChange={(e) => setPatientEmail(e.target.value)}
                                placeholder="patient1@test.com"
                                required
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Demo emails: patient1@test.com, patient2@test.com, patient3@test.com
                            </p>
                        </div>

                        <div>
                            <Label htmlFor="notes">Notes (Optional)</Label>
                            <Input
                                id="notes"
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                placeholder="Additional instructions or notes"
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Medicines</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {medicines.map((medicine, index) => (
                            <div key={index} className="p-4 border rounded-lg space-y-3 relative">
                                <div className="flex justify-between items-center mb-2">
                                    <h3 className="font-semibold">Medicine #{index + 1}</h3>
                                    {medicines.length > 1 && (
                                        <Button
                                            type="button"
                                            variant="destructive"
                                            size="sm"
                                            onClick={() => handleRemoveMedicine(index)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <Label>Medicine Name *</Label>
                                        <Input
                                            value={medicine.name}
                                            onChange={(e) => handleMedicineChange(index, 'name', e.target.value)}
                                            placeholder="e.g., Dolo 650"
                                            required
                                        />
                                    </div>

                                    <div>
                                        <Label>Dosage *</Label>
                                        <Input
                                            value={medicine.dosage}
                                            onChange={(e) => handleMedicineChange(index, 'dosage', e.target.value)}
                                            placeholder="e.g., 1-0-1 or 2 tablets"
                                            required
                                        />
                                    </div>

                                    <div>
                                        <Label>Duration</Label>
                                        <Input
                                            value={medicine.duration}
                                            onChange={(e) => handleMedicineChange(index, 'duration', e.target.value)}
                                            placeholder="e.g., 5 days"
                                        />
                                    </div>

                                    <div>
                                        <Label>Instructions</Label>
                                        <Input
                                            value={medicine.instructions}
                                            onChange={(e) => handleMedicineChange(index, 'instructions', e.target.value)}
                                            placeholder="e.g., After meals"
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}

                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleAddMedicine}
                            className="w-full"
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Add Medicine
                        </Button>
                    </CardContent>
                </Card>

                <div className="flex gap-4">
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Issuing...' : 'Issue Prescription'}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => navigate('/dashboard')}>
                        Cancel
                    </Button>
                </div>
            </form>
        </div>
    );
}
