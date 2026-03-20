import axios from 'axios';

const BASE_URL = 'http://localhost:5000';
const API_BASE_URL = `${BASE_URL}/api`;

class PredictionService {
    /**
     * Send video file for recognition
     * @param {File} videoFile 
     * @returns {Promise}
     */
    async recognize(videoFile, language = 'en') {
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('language', language);

        try {
            const response = await axios.post(`${API_BASE_URL}/recognize`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Recognition error:', error);
            throw error;
        }
    }

    /**
     * Get system information and supported terms
     */
    async getInfo() {
        try {
            const response = await axios.get(`${API_BASE_URL}/info`);
            return response.data;
        } catch (error) {
            console.error('Info error:', error);
            return { success: false, medical_terms: [] };
        }
    }

    /**
     * Get system stats
     */
    async getStats() {
        try {
            const response = await axios.get(`${API_BASE_URL}/stats`);
            return response.data;
        } catch (error) {
            console.error('Stats error:', error);
            return { status: 'offline' };
        }
    }

    /**
     * Get full audio URL from relative path
     * @param {string} relativePath 
     * @returns {string}
     */
    getFullAudioUrl(relativePath) {
        if (!relativePath) return null;
        if (relativePath.startsWith('http')) return relativePath;
        return `${BASE_URL}${relativePath}`;
    }
}

export default new PredictionService();
export { BASE_URL, API_BASE_URL };
