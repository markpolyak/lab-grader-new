import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getLabs } from '../api';

const GroupList = () => {
  const { courseId, groupId } = useParams();
  const [labs, setLabs] = useState([]);

  useEffect(() => {
    getLabs(courseId, groupId)
      .then(response => setLabs(response.data))
      .catch(error => console.error('Error fetching labs:', error));
  }, [courseId, groupId]);

  return (
    <div className='container'>
      <nav className="navbar bg-body-tertiary container">
        <div className="container-fluid">
          <a className="navbar-brand">
          <img src="/guap-desc-line.svg" alt="Logo" width="500" height="75" class="d-inline-block align-text-top"/>
          </a>
        </div>
      </nav>
      <br/>
      <h3 className='text-center'>Лабораторные работы группы {groupId}</h3>
      <br/>
      <div className="list-group container card text-bg-primary mb-3">
        {labs.map(lab => (
            <Link className='list-group-item list-group-item-action icon-link icon-link-hover'
            key={lab} to={`/courses/${courseId}/groups/${groupId}/labs/${lab}/grade`}>
              {lab}
              </Link>
        ))}
      </div>
      <br/>
      <div className='container'>
          <Link to={`/courses/${courseId}/groups/${groupId}/register`}>
            <button className="btn btn-primary">Зарегистрировать студента</button>
          </Link>
      </div>
    </div>
  );
}

export default GroupList;