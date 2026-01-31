import { useState, useCallback } from 'react';
// import { useDropzone } from 'react-dropzone'; 
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload as UploadIcon, FileText, Check, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { uploadPrescription } from '@/services/api';
import { useNavigate } from 'react-router-dom';

export default function Upload() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploading, setUploading] = useState(false);
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await uploadPrescription(formData);
            navigate(`/review/${res.data.id}`);
        } catch (err) {
            alert("Upload failed");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="container max-w-4xl py-10 mx-auto">
            <Card>
                <CardHeader>
                    <CardTitle>Upload Prescription</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-10 text-center hover:bg-accent transition-colors relative overflow-hidden">
                        {!preview ? (
                            <>
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    onChange={handleFileChange}
                                />
                                <UploadIcon className="mx-auto h-12 w-12 text-muted-foreground" />
                                <p className="mt-2 text-sm text-muted-foreground">Drag and drop or click to upload</p>
                            </>
                        ) : (
                            <div className="relative">
                                <img src={preview} alt="Preview" className="max-h-[400px] mx-auto rounded-md shadow-md" />
                                {uploading && (
                                    <motion.div
                                        className="absolute inset-0 bg-primary/20"
                                        initial={{ top: '0%' }}
                                        animate={{ top: '100%' }}
                                        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                        style={{ height: '5px', background: 'linear-gradient(to right, transparent, #3b82f6, transparent)' }}
                                    />
                                )}
                                {uploading && (
                                    <div className="absolute inset-0 flex items-center justify-center bg-black/40 text-white font-bold rounded-md">
                                        Processing OCR...
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => { setFile(null); setPreview(null); }}>Clear</Button>
                        <Button onClick={handleUpload} disabled={!file || uploading}>
                            {uploading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <UploadIcon className="mr-2 h-4 w-4" />}
                            Upload & Process
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
