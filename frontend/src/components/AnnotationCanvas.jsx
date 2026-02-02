import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Save, Trash2, Plus } from 'lucide-react';

/**
 * Interactive annotation canvas for drawing bounding boxes on prescription images
 * Adapted from Medecoder's annotation tool
 */
export default function AnnotationCanvas({ imageUrl, initialAnnotations = [], onSave }) {
    const canvasRef = useRef(null);
    const [annotations, setAnnotations] = useState(initialAnnotations);
    const [isDrawing, setIsDrawing] = useState(false);
    const [currentBox, setCurrentBox] = useState(null);
    const [imageLoaded, setImageLoaded] = useState(false);
    const imgRef = useRef(null);

    useEffect(() => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => {
            imgRef.current = img;
            setImageLoaded(true);
            drawCanvas();
        };
        img.src = imageUrl;
    }, [imageUrl]);

    useEffect(() => {
        if (imageLoaded) drawCanvas();
    }, [annotations, imageLoaded]);

    const drawCanvas = () => {
        const canvas = canvasRef.current;
        if (!canvas || !imgRef.current) return;

        const ctx = canvas.getContext('2d');
        const img = imgRef.current;

        // Set canvas size to match image
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw image
        ctx.drawImage(img, 0, 0);

        // Draw annotations
        annotations.forEach((annotation, index) => {
            const { x, y, width, height, text, confidence = 0.8 } = annotation;

            // Color based on confidence
            const color = `rgb(${Math.floor(255 * (1 - confidence))}, ${Math.floor(255 * confidence)}, 0)`;

            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);

            // Draw label
            const label = text || `Box ${index + 1}`;
            ctx.fillStyle = color;
            ctx.fillRect(x, y - 20, 100, 20);
            ctx.fillStyle = 'white';
            ctx.font = '12px Arial';
            ctx.fillText(label, x + 2, y - 5);
        });

        // Draw current box being drawn
        if (currentBox) {
            ctx.strokeStyle = '#0000ff';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.strokeRect(currentBox.x, currentBox.y, currentBox.width, currentBox.height);
            ctx.setLineDash([]);
        }
    };

    const handleMouseDown = (e) => {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        setIsDrawing(true);
        setCurrentBox({ x, y, width: 0, height: 0 });
    };

    const handleMouseMove = (e) => {
        if (!isDrawing) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;

        setCurrentBox(prev => ({
            ...prev,
            width: currentX - prev.x,
            height: currentY - prev.y
        }));
    };

    const handleMouseUp = () => {
        if (currentBox && currentBox.width !== 0 && currentBox.height !== 0) {
            const text = prompt('Enter text for this region (medicine name, dosage, etc.):');
            if (text) {
                setAnnotations([...annotations, { ...currentBox, text, confidence: 1.0 }]);
            }
        }
        setIsDrawing(false);
        setCurrentBox(null);
    };

    const handleSave = () => {
        if (onSave) {
            onSave(annotations);
        }
    };

    const handleDelete = (index) => {
        setAnnotations(annotations.filter((_, i) => i !== index));
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <span>Interactive Annotation Tool</span>
                    <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => setAnnotations([])}>
                            <Trash2 className="h-4 w-4 mr-2" /> Clear All
                        </Button>
                        <Button size="sm" onClick={handleSave}>
                            <Save className="h-4 w-4 mr-2" /> Save Annotations
                        </Button>
                    </div>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Click and drag to draw bounding boxes around text regions. Each box can be labeled with extracted text.
                    </p>

                    <div className="border rounded-lg overflow-auto max-h-[600px]">
                        <canvas
                            ref={canvasRef}
                            className="cursor-crosshair"
                            onMouseDown={handleMouseDown}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                            onMouseLeave={handleMouseUp}
                        />
                    </div>

                    <div className="mt-4">
                        <h4 className="font-semibold mb-2">Annotations ({annotations.length})</h4>
                        <div className="space-y-2 max-h-40 overflow-auto">
                            {annotations.map((ann, index) => (
                                <div key={index} className="flex items-center justify-between p-2 border rounded text-sm">
                                    <span>{ann.text || `Box ${index + 1}`}</span>
                                    <Button size="sm" variant="ghost" onClick={() => handleDelete(index)}>
                                        <Trash2 className="h-3 w-3" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
