import React from 'react';

const InpMes = ({pageChoose, message, filter, setFilter}) => {
    return (
        <div className="inpDiv">
            {pageChoose < 4 && <input className={"inpFilter"} placeholder={"Введите название..."} value={filter} onChange={(e) => setFilter(e.target.value)}/>}
            {message && pageChoose > 3 && <div className={"mes"} style={{backgroundColor: pageChoose === 5 ? "#3C393D21" : "red"}}>{message}</div>}
        </div>
    );
};

export default InpMes;