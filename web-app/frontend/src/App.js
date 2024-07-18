import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CourseList from './components/CourseList';
import CourseDetail from './components/CourseDetails';
import GroupList from './components/GroupList';
import LabList from './components/LabList';
import RegisterForm from './components/RegisterForm';
import LabGrade from './components/LabGrade'


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/courses/" element={<CourseList />} />
        <Route path="/courses/:courseId" element={<CourseDetail />} />
        <Route path="/courses/:courseId/groups" element={<GroupList />} />
        <Route path="/courses/:courseId/groups/:groupId/labs" element={<LabList />} />
        <Route path="/courses/:courseId/groups/:groupId/register" element={<RegisterForm />} />
        <Route path="/courses/:courseId/groups/:groupId/labs/:labId/grade" element={<LabGrade />} />
      </Routes>
    </Router>
  );
}

export default App;
