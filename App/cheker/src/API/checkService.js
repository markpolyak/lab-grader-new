import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000'
});
export default class checkService {
    static async getCourses(){
        const response = await api.get("/courses", {});
        return response.data
    }

    static async getGroups(course_id){
        const response = await api.get(`/courses/${course_id}/groups`, {});
        return response.data
    }

    static async getLabs(course_id, group_id){
        const response = await api.get(`/courses/${course_id}/groups/${group_id}/labs`, {});
        return response
    }

    static async postRegister(course_id, group_id, {surname, name, patronymic, github}){
        const response = await api.post(`/courses/${course_id}/groups/${group_id}/register`, {
         name, surname, patronymic, github
        });
        return response
    }

    static async postGrade(course_id, groups_id, lab_id, github){
        const response = await api.post(`/courses/${course_id}/groups/${groups_id}/labs/${lab_id}/grade`, {
            github
        });
        return response


    }
}