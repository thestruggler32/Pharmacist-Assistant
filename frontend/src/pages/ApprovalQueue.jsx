import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';
import axios from '@/services/api';
import { useNavigate } from 'react-router-dom';

/**
 * Pharmacist Approval Queue - displays low-confidence prescriptions needing review
 * Adapted from Medecoder's review network system
 */
export default function ApprovalQueue() {
    const [approvals, setApprovals] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchApprovals();
    }, []);

    const fetchApprovals = async () => {
        try {
            const response = await axios.get('/api/approvals');
            setApprovals(response.data.approvals || []);
        } catch (error) {
            console.error('Failed to fetch approvals:', error);
        } finally {
            setLoading(false);
        }
    };

    const getConfidenceBadge = (confidence) => {
        if (confidence >= 0.8) return <Badge className="bg-green-500">High</Badge>;
        if (confidence >= 0.6) return <Badge className="bg-yellow-500">Medium</Badge>;
        return <Badge className="bg-red-500">Low</Badge>;
    };

    if (loading) {
        return <div className="p-8 text-center">Loading approval queue...</div>;
    }

    return (
        <div className="container py-8 max-w-6xl mx-auto">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                            <AlertTriangle className="h-6 w-6 text-yellow-500" />
                            Pharmacist Approval Queue
                        </span>
                        <Badge variant="outline">{approvals.length} Pending</Badge>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {approvals.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                            <p className="text-lg font-semibold">All caught up!</p>
                            <p>No prescriptions need review at this time.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {approvals.map((approval) => {
                                const prescription = approval.prescription || {};
                                return (
                                    <Card key={approval.id} className="border-l-4 border-l-yellow-500">
                                        <CardContent className="p-4">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <h3 className="font-semibold">
                                                            Prescription #{prescription.id?.slice(0, 8)}
                                                        </h3>
                                                        {getConfidenceBadge(prescription.confidence || 0)}
                                                        <Badge variant="outline">
                                                            <Clock className="h-3 w-3 mr-1" />
                                                            {new Date(approval.created_at).toLocaleDateString()}
                                                        </Badge>
                                                    </div>

                                                    <div className="text-sm text-muted-foreground space-y-1">
                                                        <p>Uploaded by: {prescription.uploaded_by || 'Unknown'}</p>
                                                        <p>Confidence Score: {((prescription.confidence || 0) * 100).toFixed(0)}%</p>
                                                        <p>Medicines Detected: {prescription.medicines?.length || 0}</p>
                                                    </div>

                                                    {prescription.medicines && prescription.medicines.length > 0 && (
                                                        <div className="mt-3 p-2 bg-muted rounded text-sm">
                                                            <strong>Preview:</strong>
                                                            <ul className="list-disc list-inside mt-1">
                                                                {prescription.medicines.slice(0, 3).map((med, i) => (
                                                                    <li key={i}>{med.medicine_name || med.name}</li>
                                                                ))}
                                                                {prescription.medicines.length > 3 && (
                                                                    <li className="text-muted-foreground">
                                                                        +{prescription.medicines.length - 3} more...
                                                                    </li>
                                                                )}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>

                                                <div className="flex flex-col gap-2">
                                                    <Button
                                                        size="sm"
                                                        onClick={() => navigate(`/review/${prescription.id}?approval=${approval.id}`)}
                                                    >
                                                        Review
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
