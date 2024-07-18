import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000'
});

export const getCourses = () => api.get('/courses');
export const getCourse = (courseId) => api.get(`/courses/${courseId}`);
export const getGroups = (courseId) => api.get(`/courses/${courseId}/groups`);
export const getLabs = (courseId, groupId) => api.get(`/courses/${courseId}/groups/${groupId}/labs`);
export const registerStudent = (courseId, groupId, data) => api.post(`/courses/${courseId}/groups/${groupId}/register`, data);
export const gradeLab = (courseId, groupId, labId, data) => api.post(`/courses/${courseId}/groups/${groupId}/labs/${labId}/grade`, data);

export default api;