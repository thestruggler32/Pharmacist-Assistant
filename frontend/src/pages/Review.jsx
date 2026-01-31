import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getPrescription, translateText } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'; // Need to create Table component or use standard HTML
import { Button } from '@/components/ui/button';
import { Loader2, Download, Languages } from 'lucide-react';

export default function Review() {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [translated, setTranslated] = useState(false);

    const handleTranslate = async () => {
        if (translated) {
            // Revert (reload data or just toggle flag if we stored original)
            // For simplicity, just reload
            getPrescription(id).then(res => setData(res.data));
            setTranslated(false);
            return;
        }

        const newMedicines = await Promise.all(data.medicines.map(async (med) => {
            const transName = await translateText(med.medicine_name || med.name || '', 'hi');
            return { ...med, medicine_name: transName.data.translatedText + ` (${med.medicine_name || med.name})` };
        }));

        setData({ ...data, medicines: newMedicines });
        setTranslated(true);
    };

    useEffect(() => {
        getPrescription(id).then(res => setData(res.data)).catch(console.error);
    }, [id]);

    if (!data) return <div className="flex justify-center p-10"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="container py-8 max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Image Side */}
                <Card>
                    <CardHeader><CardTitle>Original Prescription</CardTitle></CardHeader>
                    <CardContent>
                        <img src={data.image_url} alt="Prescription" className="w-full rounded-md" />
                    </CardContent>
                </Card>

                {/* Results Side */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Extracted Medicines</CardTitle>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={handleTranslate}>
                                <Languages className="h-4 w-4 mr-2" /> {translated ? 'Original' : 'Translate (Hi)'}
                            </Button>
                            <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" /> Export</Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Medicine</TableHead>
                                        <TableHead>Dosage</TableHead>
                                        <TableHead>Duration</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {data.medicines && data.medicines.map((med, i) => (
                                        <TableRow key={i}>
                                            <TableCell className="font-medium">{med.medicine_name || med.name}</TableCell>
                                            <TableCell>{med.dosage}</TableCell>
                                            <TableCell>{med.duration || '-'}</TableCell>
                                        </TableRow>
                                    ))}
                                    {(!data.medicines || data.medicines.length === 0) && (
                                        <TableRow>
                                            <TableCell colSpan={3} className="text-center text-muted-foreground">No medicines detected</TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </div>

                        <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-md border border-yellow-200 dark:border-yellow-800">
                            <h4 className="font-semibold text-yellow-800 dark:text-yellow-500 mb-1">Confidence Score</h4>
                            <div className="flex items-center gap-2">
                                <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                                    <div className="h-full bg-green-500 w-[85%]" />
                                </div>
                                <span className="text-sm font-bold">85%</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
