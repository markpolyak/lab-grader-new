import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getGroups } from '../api';


const GroupList = () => {
    const { courseId } = useParams();
    const [groups, setGroups] = useState([]);
  
    useEffect(() => {
        getGroups(courseId)
        .then(response => setGroups(response.data))
        .catch(error => console.error('Error fetching courses:', error));
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
        <h2 className='text-center'>Группы</h2>
        <br/>
        <div className="list-group container card text-bg-primary mb-3">
        {groups.map(group => (
            <Link className='list-group-item list-group-item-action' key={group} to={`/courses/${courseId}/groups/${group}/labs`}>{group}</Link>
        ))}
      </div>
      </div>
    );
  }
  
  export default GroupList;