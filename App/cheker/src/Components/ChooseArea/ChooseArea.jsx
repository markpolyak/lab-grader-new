import React from 'react';

const ChooseArea = ({allOpt, courses, setCourse, groups, setGroup, labs,setLab, strfilt}) => {
    return (
        <div className={"divOpts"}>
            {[...courses].filter(p => p.name.toLowerCase().includes(strfilt.toLowerCase())).map((a) => <div
                key={a.id}
                className={a.id === allOpt[0].id ? "options optAct" : "options"}
                onClick={() => {
                    setCourse(a);
                }}
            >
                {a.name} - семестр: {a.semester} {a.email}
            </div>)}
            {[...groups].filter(p=>p.toLowerCase().includes(strfilt.toLowerCase())).map((a) => <div key={a} className={a === allOpt[1] ? "options optAct" : "options"} onClick={(e) => {
                setGroup(a)}
            }>{a}</div>)}
            {[...labs].filter(p=>p.toLowerCase().includes(strfilt.toLowerCase())).map((a) => <div key={a} className={a === allOpt[2] ? "options optAct" : "options"} onClick={(e) => {
                setLab(a)}
            }>ЛР{a}</div>)}

        </div>
    );
};

export default ChooseArea;