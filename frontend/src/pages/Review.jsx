import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPrescription, API_BASE_URL } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

import { Loader2, Check, X, Plus, Trash2, Image as ImageIcon, PencilRuler } from 'lucide-react';
import AnnotationCanvas from '@/components/AnnotationCanvas';
import axios from 'axios';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";

export default function Review() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [medicines, setMedicines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const u = localStorage.getItem('user');
        if (u) setUser(JSON.parse(u));
    }, []);
    const [saving, setSaving] = useState(false);
    const [showAnnotation, setShowAnnotation] = useState(false);

    // Alternatives State
    const [showAlternatives, setShowAlternatives] = useState(false);
    const [alternativesData, setAlternativesData] = useState(null);
    const [findingAlternatives, setFindingAlternatives] = useState(false);
    const [searchLocality, setSearchLocality] = useState('');

    useEffect(() => {
        getPrescription(id)
            .then(res => {
                setData(res.data);
                setMedicines(res.data.medicines || []);
                setLoading(false);
            })
            .catch(console.error);
    }, [id]);

    const handleCellEdit = (index, field, value) => {
        const updated = [...medicines];
        updated[index][field] = value;
        setMedicines(updated);
    };

    const handleAddRow = () => {
        setMedicines([...medicines, {
            medicine_name: '',
            dosage: '',
            duration: ''
        }]);
    };

    const handleDeleteRow = (index) => {
        setMedicines(medicines.filter((_, i) => i !== index));
    };

    const handleApprove = async () => {
        setSaving(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/api/prescriptions/${id}/approve`,
                { medicines },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            alert('Prescription approved successfully!');
            navigate('/dashboard');
        } catch (error) {
            console.error('Approve failed:', error);
            alert('Failed to approve prescription');
        } finally {
            setSaving(false);
        }
    };

    const handleReject = async () => {
        const reason = prompt('Reason for rejection:');
        if (!reason) return;

        setSaving(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/api/prescriptions/${id}/reject`,
                { reason },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            alert('Prescription rejected');
            navigate('/dashboard');
        } catch (error) {
            console.error('Reject failed:', error);
            alert('Failed to reject prescription');
        } finally {
            setSaving(false);
        }
    };

    const handleSaveAnnotations = async (annotations) => {
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/api/prescriptions/${id}/annotate`,
                { annotations },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            alert('Annotations saved successfully!');
            setShowAnnotation(false);
        } catch (error) {
            console.error('Failed to save annotations:', error);
            alert('Failed to save annotations');
        }
    };

    const handleShowAlternatives = async (medicineName, overrideLocality = null) => {
        if (!medicineName) return;

        setShowAlternatives(true);
        setFindingAlternatives(true);
        // Don't clear data immediately if updating, to prevent flicker
        if (!overrideLocality) setAlternativesData(null);

        try {
            const token = localStorage.getItem('token');
            // Use override if provided (User Update), else User defaults
            const locality = overrideLocality || user?.locality || '';

            // Sync state
            if (!searchLocality) setSearchLocality(locality);

            const response = await axios.post('/api/medicines/alternatives',
                {
                    medicine_name: medicineName,
                    locality: locality
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setAlternativesData(response.data);
            // Update input to reflect what was actually used/detected
            if (response.data.locality) setSearchLocality(response.data.locality);

        } catch (error) {
            console.error('Failed to find alternatives:', error);
            // Show error state in modal if needed, or just alert
            setAlternativesData({
                original: medicineName,
                alternatives: [],
                message: "Failed to fetch alternatives"
            });
        } finally {
            setFindingAlternatives(false);
        }
    };

    const handleUpdateLocality = () => {
        if (alternativesData?.original) {
            handleShowAlternatives(alternativesData.original, searchLocality);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        );
    }

    if (!data) {
        return <div className="p-8 text-center">Prescription not found</div>;
    }

    const statusColor = {
        'pending': 'bg-yellow-500',
        'approved': 'bg-green-500',
        'rejected': 'bg-red-500'
    };

    return (
        <div className="container mx-auto p-6 max-w-7xl">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Review Prescription</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Uploaded by {data.uploaded_by} on {new Date(data.timestamp).toLocaleDateString()}
                    </p>
                </div>
                <Badge className={statusColor[data.status]}>
                    {data.status.toUpperCase()}
                </Badge>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                <ImageIcon className="h-5 w-5" />
                                Prescription Image
                            </CardTitle>
                            <Button
                                onClick={() => setShowAnnotation(!showAnnotation)}
                                variant={showAnnotation ? "default" : "outline"}
                                size="sm"
                            >
                                <PencilRuler className="h-4 w-4 mr-1" />
                                {showAnnotation ? 'Hide' : 'Show'} Annotations
                            </Button>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            <strong>Annotation Tool:</strong> Draw bounding boxes to mark medicines on the image and verify OCR accuracy
                        </p>
                    </CardHeader>
                    <CardContent>
                        {showAnnotation && data.image_url ? (
                            <AnnotationCanvas
                                imageUrl={`${API_BASE_URL}${data.image_url}`}
                                onSave={handleSaveAnnotations}
                            />
                        ) : data.image_url ? (
                            <img
                                src={`${API_BASE_URL}${data.image_url}`}
                                alt="Prescription"
                                className="w-full rounded-lg shadow-md hover:shadow-xl transition-shadow"
                            />
                        ) : (
                            <div className="bg-gray-100 h-96 flex items-center justify-center rounded-lg">
                                <p className="text-gray-500">No image available</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle>Extracted Medicines</CardTitle>
                            <Button onClick={handleAddRow} disabled={user?.role !== 'pharmacist'} variant="outline" size="sm">
                                <Plus className="h-4 w-4 mr-1" />
                                Add Medicine
                            </Button>
                        </div>
                        <p className="text-sm text-gray-500 mt-2">
                            Review and edit medicines before approving
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {medicines.length === 0 ? (
                                <p className="text-center text-gray-500 py-8">
                                    No medicines found. Click Add Medicine to add manually.
                                </p>
                            ) : (
                                medicines.map((med, idx) => (
                                    <div key={idx} className="p-3 border rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                                        <div className="flex items-start justify-between mb-2">
                                            <span className="text-sm font-medium text-gray-500">#{idx + 1}</span>
                                            <div className="flex gap-1">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    title="Find Alternatives"
                                                    onClick={() => handleShowAlternatives(med.medicine_name || med.name)}
                                                    className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800"
                                                >
                                                    <PencilRuler className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handleDeleteRow(idx)}
                                                    className="h-6 w-6 p-0"
                                                    disabled={user?.role !== 'pharmacist'}
                                                >
                                                    <Trash2 className={`h-4 w-4 text-red-500 ${user?.role !== 'pharmacist' ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}`} />
                                                </Button>
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <input readOnly={user?.role !== 'pharmacist'}
                                                placeholder="Medicine name"
                                                value={med.medicine_name || med.name || ''}
                                                onChange={(e) => handleCellEdit(idx, 'medicine_name', e.target.value)}
                                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-medium"
                                            />
                                            <div className="grid grid-cols-2 gap-2">
                                                <input readOnly={user?.role !== 'pharmacist'}
                                                    placeholder="Dosage"
                                                    value={med.dosage || ''}
                                                    onChange={(e) => handleCellEdit(idx, 'dosage', e.target.value)}
                                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                                />
                                                <input readOnly={user?.role !== 'pharmacist'}
                                                    placeholder="Duration"
                                                    value={med.duration || ''}
                                                    onChange={(e) => handleCellEdit(idx, 'duration', e.target.value)}
                                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600">
                            {medicines.length} medicine(s) &middot;
                            {data.status === 'pending' ? ' Awaiting your review' : ` ${data.status} prescription`}
                        </div>
                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                onClick={handleReject}
                                disabled={saving || data.status !== 'pending' || user?.role !== 'pharmacist'}
                                className="border-red-500 text-red-500 hover:bg-red-50"
                            >
                                <X className="h-4 w-4 mr-2" />
                                Reject
                            </Button>
                            <Button
                                onClick={handleApprove}
                                disabled={saving || data.status !== 'pending' || user?.role !== 'pharmacist'}
                                className="bg-green-600 hover:bg-green-700"
                            >
                                {saving ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                ) : (
                                    <Check className="h-4 w-4 mr-2" />
                                )}
                                Approve & Save
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
            {/* Alternatives Modal */}
            <Dialog open={showAlternatives} onOpenChange={setShowAlternatives}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Regional Alternatives</DialogTitle>
                        <DialogDescription>
                            Find available medicines in your region.
                        </DialogDescription>
                    </DialogHeader>

                    {findingAlternatives ? (
                        <div className="flex justify-center p-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            <span className="ml-2 mt-1">Finding best matches for your locality...</span>
                        </div>
                    ) : alternativesData ? (
                        <div className="space-y-4">
                            <div className="bg-slate-50 p-3 rounded-md border flex justify-between">
                                <div>
                                    <span className="text-xs text-muted-foreground block">Looking for:</span>
                                    <span className="font-medium text-lg">{alternativesData.original}</span>
                                </div>
                                <div className="text-right flex items-center gap-2">
                                    <div className="flex flex-col items-end">
                                        <span className="text-xs text-muted-foreground mb-1">Delivering to:</span>
                                        <div className="flex gap-2">
                                            <input
                                                value={searchLocality || ''}
                                                onChange={(e) => setSearchLocality(e.target.value)}
                                                className="flex h-8 w-48 rounded-md border border-input bg-background px-3 py-2 text-sm text-right"
                                                placeholder="Enter Locality"
                                            />
                                            <Button
                                                size="sm"
                                                variant="secondary"
                                                onClick={handleUpdateLocality}
                                                disabled={findingAlternatives}
                                                className="h-8"
                                            >
                                                Update
                                            </Button>
                                        </div>
                                        <span className="text-[10px] text-green-600 mt-1">
                                            {alternativesData?.hub_detected ? `Success: Mapped to ${alternativesData.hub_detected} Hub` : ''}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="border rounded-md overflow-hidden">
                                <table className="w-full text-sm">
                                    <thead className="bg-muted">
                                        <tr>
                                            <th className="p-2 text-left">Brand Name</th>
                                            <th className="p-2 text-left">Region</th>
                                            <th className="p-2 text-left">Strength</th>
                                            <th className="p-2 text-right">Availability</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {alternativesData && alternativesData.alternatives && alternativesData.alternatives.length > 0 ? (
                                            alternativesData.alternatives.map((alt, i) => (
                                                <tr key={i} className="border-t hover:bg-slate-50">
                                                    <td className="p-2 font-medium">{alt.brand_name}</td>
                                                    <td className="p-2">{alt.region}</td>
                                                    <td className="p-2 text-xs">{alt.strength}</td>
                                                    <td className="p-2 text-right">
                                                        <Badge variant={alt.availability.includes('Local') ? 'default' : 'secondary'}>
                                                            {alt.availability}
                                                        </Badge>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan={4} className="p-4 text-center text-muted-foreground">
                                                    No regional alternatives found.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            <p className="text-xs text-muted-foreground text-center">
                                * Generic: {alternativesData.generic_name}
                            </p>
                        </div>
                    ) : null}
                </DialogContent>
            </Dialog>
        </div>
    );
}





