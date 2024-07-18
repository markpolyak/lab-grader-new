import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { registerStudent, gradeLab } from '../api';

const RegisterAndGradeForm = () => {
    const { courseId, groupId, labId } = useParams();
    const [student, setStudent] = useState({ surname: '', name: '', patronymic: '', github: '' });
    const [messages, setMessages] = useState([]);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setStudent((prev) => ({ ...prev, [name]: value }));
    };

    const validateFields = () => {
        const { surname, name, github } = student;
        return surname.trim().length > 0 && name.trim().length > 0 && github.trim().length > 0;
    };

    const handleRegisterAndGrade = async () => {
        if (!validateFields()) {
            setError('Все поля должны быть обязательно заполнены (кроме Отчества).');
            setMessages([]);
            return;
        }

        setError('');
        setMessages([]);

        try {
            const registerResponse = await registerStudent(courseId, groupId, student);
            setMessages(prev => [...prev, registerResponse.data.message]);

            if (registerResponse.status === 200 || registerResponse.status === 422) {
                try {
                    const gradeResponse = await gradeLab(courseId, groupId, labId, { github: student.github });
                    setMessages(prev => [...prev, gradeResponse.data.message]);
                } catch (error) {
                    setError(error.response.data.detail);
                }
            }
            setStudent({ surname: '', name: '', patronymic: '', github: '' }); 
        } catch (error) {
            setError(error.response.data.detail);
        }
    };

    const getAlertClass = (message) => {
        if (message === "Аккаунт GitHub успешно задан" || message === "Лабораторная работа оценена успешно") {
            return "alert alert-success";
        }
        return "alert alert-warning";
    };

    return (
        <div className='container'>
            <nav className="navbar bg-body-tertiary">
                <div className="container-fluid">
                    <a className="navbar-brand">
                        <img src="/guap-desc-line.svg" alt="Logo" width="500" height="75" className="d-inline-block align-text-top"/>
                    </a>
                </div>
            </nav>
            <div className='container'>
                <h3>Регистрация и проверка лабораторной работы группы {groupId}</h3>
                <div className="mb-3">
                    <label className="form-label">Фамилия:</label>
                    <input className='form-control' type="text" name="surname" value={student.surname} onChange={handleChange} />
                </div>
                <div className="mb-3">
                    <label className="form-label">Имя:</label>
                    <input className='form-control' type="text" name="name" value={student.name} onChange={handleChange} />
                </div>
                <div className="mb-3">
                    <label className="form-label">Отчество:</label>
                    <input className='form-control' type="text" name="patronymic" value={student.patronymic} onChange={handleChange} />
                </div>
                <div className="mb-3">
                    <label className="form-label">GitHub:</label>
                    <input className='form-control' type="text" name="github" value={student.github} onChange={handleChange} />
                </div>
                <button className='btn btn-primary' onClick={handleRegisterAndGrade}>Зарегистрировать и проверить</button>
                <br/>
                <br/>
                {messages.length > 0 && messages.map((msg, index) => (
                    <div key={index} className={getAlertClass(msg)} role="alert">{msg}</div>
                ))}
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
            </div>
        </div>
    );
}

export default RegisterAndGradeForm;