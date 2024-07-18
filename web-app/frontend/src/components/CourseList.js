import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const CourseList = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    api.get('/courses/')
      .then(response => setCourses(response.data))
      .catch(error => console.error('Error fetching courses:', error));
  }, []);

  return (
    <div className='container'>
      <nav className="navbar bg-body-tertiary">
        <div className="container-fluid">
          <a className="navbar-brand">
          <img src="/guap-desc-line_blue.svg" alt="Logo" width="500" height="75" class="d-inline-block align-text-top"/>
          </a>
        </div>
      </nav>
      <br/>
      <h2 className='text-center'>Доступные курсы</h2>
      <br/>
      <div className="list-group container-md card text-bg-primary mb-3">
        {courses.map(course => (
            <Link className='list-group-item list-group-item-action' key={course.id} to={`/courses/${course.id}`}>{course.name} ({course.semester})</Link>
        ))}
      </div>
    </div>
  );
}

export default CourseList;