import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCourse, getGroups } from '../api';

const CourseDetail = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [groups, setGroups] = useState([]);

  useEffect(() => {
    getCourse(courseId)
      .then(response => setCourse(response.data))
      .catch(error => console.error('Error fetching course details:', error));
  }, [courseId]);


  return (
    <div className='container'>
      <nav className="navbar bg-body-tertiary">
        <div className="container-fluid">
          <a className="navbar-brand">
          <img src="/guap-desc-line.svg" alt="Logo" width="500" height="75" class="d-inline-block align-text-top"/>
          </a>
        </div>
      </nav>
      <br/>
      <div className='container'>
        <h2 className='text-center'>{course.name}</h2>
        <br/>
        <ul className='list-group list-group-flush card text-bg-primary mb-3'>
          <li className="list-group-item">Идентификатор: {course.id}</li>
          <li className="list-group-item">Файл конфигурации: {course.config}</li>
          <li className="list-group-item">Семестр: {course.semester}</li>
          <li className="list-group-item">Почта: {course.email}</li>
          <li className="list-group-item">GitHub: {course['github-organization']}</li>
          <li className="list-group-item">Google Spreadsheet: {course['google-spreadsheet']}</li>
        </ul>
      </div>
      <br/>
      <div className='container'>
          <Link to={`/courses/${courseId}/groups`}>
            <button className="btn btn-primary">Посмотреть группы</button>
          </Link>
      </div>
    </div>
  );
}

export default CourseDetail;