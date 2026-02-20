import { useState, useEffect } from 'react';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList, Legend } from 'recharts';
import { Upload, Download, ChartBar, Activity, CheckCircle, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Get API URL from env or default
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

interface ModelMetrics {
    inertias: number[];
    silhouette_scores: number[];
    optimal_k: number;
}

interface UploadResponse {
    message: string;
    n_clusters: number;
    rows: number;
    columns: string[];
    model_metrics: ModelMetrics;
}

interface CustomerData {
    Cluster: number;
    CustomerSegment: string;
    [key: string]: any;
}

interface Insight {
    label: string;
    count: number;
    description: string;
    stats: Record<string, number>;
}

function App() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [metrics, setMetrics] = useState<UploadResponse | null>(null);
    const [data, setData] = useState<CustomerData[]>([]);
    const [insights, setInsights] = useState<Record<string, Insight>>({});
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post(`${API_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setMetrics(res.data);
            await fetchClusters();
            await fetchInsights();
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during upload.");
        } finally {
            setLoading(false);
        }
    };

    const fetchClusters = async () => {
        try {
            const res = await axios.get(`${API_URL}/clusters`);
            setData(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchInsights = async () => {
        try {
            const res = await axios.get(`${API_URL}/insights`);
            setInsights(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleDownload = async () => {
        try {
            const response = await axios.get(`${API_URL}/download`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'segmented_customers.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error(err);
            setError("Failed to download report.");
        }
    };

    // Choose colors for clusters
    const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6366f1'];

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-8">
            <div className="max-w-7xl mx-auto space-y-12">

                {/* Header */}
                <header className="text-center space-y-4">
                    <motion.h1
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-4xl md:text-5xl font-extrabold tracking-tight text-gray-900"
                    >
                        Customer Segmentation <span className="text-blue-600">AI</span>
                    </motion.h1>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Upload your transaction data to automatically group customers using K-Means clustering.
                    </p>
                </header>

                {/* Upload Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100"
                >
                    <div
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer"
                    >
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            className="hidden"
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-4">
                            <div className="bg-blue-100 p-4 rounded-full text-blue-600">
                                <Upload size={32} />
                            </div>
                            <div>
                                <span className="text-lg font-semibold text-gray-700">
                                    {file ? file.name : "Click to select or drag and drop CSV"}
                                </span>
                                <p className="text-sm text-gray-500 mt-1">Recommended: Annual Income, Spending Score</p>
                            </div>
                        </label>
                    </div>

                    <div className="mt-6 flex justify-center">
                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className={`px-8 py-3 rounded-lg font-semibold text-white shadow-lg transition-all ${!file || loading
                                    ? 'bg-gray-400 cursor-not-allowed'
                                    : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-500/30'
                                }`}
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <Activity className="animate-spin" size={20} /> Processing...
                                </span>
                            ) : (
                                "Analyze Segments"
                            )}
                        </button>
                    </div>

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg text-center border border-red-100">
                            {error}
                        </div>
                    )}
                </motion.div>

                {/* Results Section */}
                {metrics && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-8"
                    >
                        {/* Metrics Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
                                <h3 className="text-gray-500 font-medium mb-2">Optimal Clusters (K)</h3>
                                <p className="text-4xl font-bold text-blue-600">{metrics.model_metrics.optimal_k}</p>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
                                <h3 className="text-gray-500 font-medium mb-2">Total Customers</h3>
                                <p className="text-4xl font-bold text-green-600">{metrics.rows}</p>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
                                <h3 className="text-gray-500 font-medium mb-2">Silhouette Score</h3>
                                <p className="text-4xl font-bold text-purple-600">
                                    {metrics.model_metrics.silhouette_scores[metrics.model_metrics.optimal_k - 2]?.toFixed(3) || "N/A"}
                                </p>
                            </div>
                        </div>

                        {/* Charts & Insights Grid */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                            {/* Scatter Plot */}
                            <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg border border-gray-100 min-h-[500px]">
                                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                    <ChartBar className="text-blue-500" /> Customer Clusters
                                </h3>
                                <div className="h-[400px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                            <XAxis
                                                type="number"
                                                dataKey="Annual Income (k$)"
                                                name="Income"
                                                unit="k$"
                                                label={{ value: 'Annual Income (k$)', position: 'bottom', offset: 0 }}
                                            />
                                            <YAxis
                                                type="number"
                                                dataKey="Spending Score (1-100)"
                                                name="Spending"
                                                label={{ value: 'Spending Score', angle: -90, position: 'left' }}
                                            />
                                            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                                            <Legend />
                                            {Array.from({ length: metrics.model_metrics.optimal_k }).map((_, idx) => (
                                                <Scatter
                                                    key={idx}
                                                    name={insights[idx]?.label || `Cluster ${idx}`}
                                                    data={data.filter(d => d.Cluster === idx)}
                                                    fill={COLORS[idx % COLORS.length]}
                                                />
                                            ))}
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Insights Panel */}
                            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                    <Database className="text-purple-500" /> Segment Insights
                                </h3>
                                <div className="space-y-6 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                    {Object.entries(insights).map(([clusterId, insight], idx) => (
                                        <div key={clusterId} className="p-4 rounded-lg bg-gray-50 border border-gray-200">
                                            <div className="flex items-center gap-2 mb-2">
                                                <div
                                                    className="w-3 h-3 rounded-full"
                                                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                                                />
                                                <h4 className="font-semibold text-gray-800">{insight.label}</h4>
                                            </div>
                                            <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
                                            <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                                                <div>Size: <span className="font-medium text-gray-900">{insight.count}</span></div>
                                                {insight.stats['Spending Score (1-100)'] && (
                                                    <div>Spending: <span className="font-medium text-gray-900">{insight.stats['Spending Score (1-100)'].toFixed(1)}</span></div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-8 pt-6 border-t border-gray-100">
                                    <button
                                        onClick={handleDownload}
                                        className="w-full py-3 rounded-lg bg-gray-900 text-white font-medium hover:bg-gray-800 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <Download size={18} /> Download Full Report
                                    </button>
                                </div>
                            </div>

                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    )
}

export default App
