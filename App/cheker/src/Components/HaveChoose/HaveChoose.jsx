import React from 'react';

const HaveChoose = ({course, group, lab}) => {
    return (
        <div className={"userChoose"} style={course.name.length<=0 ? {display: "none"} : {}}>
            {course.name.length > 0 ? <div>{course.name} ({course.semester})</div> : null}
            {group.length > 0 ? <div>{group}</div> : null}
            {lab.length > 0 ? <div>ЛР{lab}</div> : null}
        </div>
    );
};

export default HaveChoose;