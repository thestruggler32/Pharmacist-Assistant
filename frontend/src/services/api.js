import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
            name: response.data.name,
            role: response.data.role
        }));
    }
    return response.data;
};

export const verifyLicense = (license_no) => api.post('/verify-license', { license_no });
export const uploadPrescription = (formData) => api.post('/ocr/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
});
export const getPrescription = (id) => api.get(`/prescriptions/${id}`);
export const translateText = (text, target) => api.post('/translate', { text, target });

export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
};

export default api;
