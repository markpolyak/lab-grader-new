import React from 'react';

const FormRegister = ({fullUserData, setFullUserData}) => {
    return (
            <div className={"form"}>
                    <div><input value={fullUserData.surname} onChange={(e) => setFullUserData({...fullUserData, surname: e.target.value})} placeholder={"*Фамилия.."}/></div>
                    <div><input value={fullUserData.name} onChange={(e) => setFullUserData({...fullUserData, name: e.target.value})} placeholder={"*Имя.."}/></div>
                    <div><input value={fullUserData.patronymic} onChange={(e) => setFullUserData({...fullUserData, patronymic: e.target.value})} placeholder={"Отчество.."}/></div>
                    <div><input value={fullUserData.github} onChange={(e) => setFullUserData({...fullUserData, github: e.target.value})} placeholder={"*Никнейм гитхаб.."}/></div>
            </div>

    );
};

export default FormRegister;