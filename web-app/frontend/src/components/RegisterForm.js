import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { registerStudent } from '../api';

const RegisterForm = () => {
    const { courseId, groupId } = useParams();
    const [student, setStudent] = useState({ surname: '', name: '', patronymic: '', github: '' });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setStudent((prev) => ({ ...prev, [name]: value }));
    };

    const validateFields = () => {
        const { surname, name, github } = student;
        if (surname.trim().length === 0 || name.trim().length === 0 || github.trim().length === 0) {
            return false;
        }
        return true;
    };

    const handleRegister = async () => {
        if (!validateFields()) {
            setError('Все поля должны быть обязательно заполнены (кроме Отчества).');
            setMessage('');
            return;
        }
        
        try {
            const response = await registerStudent(courseId, groupId, student);
            setMessage(response.data.message);
            setError('');
            setStudent({ surname: '', name: '', patronymic: '', github: '' });
        } catch (error) {
            setError(error.response.data.detail);
            setMessage('');
        }
    };

    const getAlertClass = () => {
        if (message === "Аккаунт GitHub успешно задан") {
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
                <h3>Зарегистрировать студента группы {groupId}</h3>
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
                    <label className="form-label"> GitHub:</label>
                    <input className='form-control' type="text" name="github" value={student.github} onChange={handleChange} />
                </div>
                <button className='btn btn-primary' onClick={handleRegister}>Зарегистрировать</button>
                <br/>
                <br/>
                {message && <div className={getAlertClass()} role="alert">{message}</div>}
                {error && <div className="alert alert-danger" role="alert">{error}</div>}
            </div>
        </div>
    );
}

export default RegisterForm;