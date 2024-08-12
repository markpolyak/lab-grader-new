import React from 'react';
import ar from "../../utils/img/arrow.png";
import cl from "./ManageArrow.module.css"

const ManageArrow = ({FUD, setFilter, pageChoose, setPageChoose, allOpt, callback}) => {
    const checkOppNext = () => {
        if (pageChoose < 4) {
            if(pageChoose === 1) {
                if (allOpt[pageChoose - 1].length > 0 || allOpt[pageChoose - 1].name.length !== 0 ) {

                    return true
                }
            }
            else {
                if (allOpt[pageChoose - 1].length > 0) {

                    return true
                }
            }
        }

        else if (pageChoose === 4){
            if (FUD.name.length > 0  && FUD.surname.length > 0 && FUD.github.length > 0){
                return true
            }
        }
    }

    return (
        <div className={"arrowDiv"}>


            <div className={pageChoose!==1 ? cl.textBut + " " +  cl.tbLeft + " " +cl.cursPoint : cl.textBut + " " +  cl.tbLeft} onClick={() =>
            {
                if (pageChoose!==1) {
                    setFilter("")
                    setPageChoose(pageChoose-1)

                }

            }

            }>
                <div className={pageChoose>1 ? cl.arDivL + " " + cl.actB : cl.arDivL }>
                    <img src={ar} style={{height: "100%"}} alt={"arrow to back"} />
                </div>

                Назад
            </div>

            <div className={cl.progress}>
                <div className={pageChoose>=1 ? cl.active : cl.desActive} onClick={() => (
                    pageChoose > 1 ? setPageChoose(1) : null

                )}></div>
                <div className={pageChoose>=2 ? cl.active : cl.desActive} onClick={() => (
                    pageChoose > 2 ? setPageChoose(2) : null

                )}></div>
                <div className={pageChoose>=3 ? cl.active : cl.desActive} onClick={() => (
                    pageChoose > 3 ? setPageChoose(3) : null

                )}></div>
                <div className={pageChoose>=4 ? cl.active : cl.desActive} onClick={() => (
                    pageChoose > 4 ? setPageChoose(4) : null

                )}></div>
                <div className={pageChoose>=5 ? cl.active : cl.desActive} onClick={() => (
                    pageChoose > 5 ? setPageChoose(5) : null

                )}></div>
            </div>

            <div className={checkOppNext() ? cl.textBut + " " + cl.cursPoint + " " + cl.tbRight : cl.textBut + " " + cl.tbRight} onClick={() => {
                if (pageChoose !== 4 && checkOppNext()) {
                            setPageChoose(pageChoose + 1)
                            setFilter("")
                }
                else if(checkOppNext()){

                    callback()
                }
            }}>Далее
                <div className={checkOppNext() ? cl.arDivR + " " + cl.actB :  cl.arDivR}>
                    <img src={ar} style={{rotate: "180deg", height: "100%"}} alt = {"arrow to next"} />
                </div>

            </div>


        </div>
    );
};

export default ManageArrow;