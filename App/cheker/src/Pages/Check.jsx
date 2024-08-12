import React, {useEffect, useState} from 'react';
import ChooseArea from "../Components/ChooseArea/ChooseArea";
import FormRegister from "../Components/FormRegister/FormRegister";
import ManageArrow from "../Components/ManageArrow/ManageArrow";
import checkService from "../API/checkService";
import Header from "../Components/Header/Header";
import HaveChoose from "../Components/HaveChoose/HaveChoose";
import InpMes from "../Components/InputAndMessage/InpMes";

const Check = () => {

    const [courses, setCourses] = useState([])
    const [course, setCourse] = useState({id: "", name: "", semester: "", email: ""})
    const [groups, setGroups] = useState([])
    const [group, setGroup] = useState("")
    const [labs, setLabs] = useState([])
    const [lab, setLab] = useState("")
    const [message, setMessage] = useState("")
    const [result, setResult] = useState("")
    const [fullUserData, setFullUserData] = useState({surname: "", name: "", patronymic: "", github: ""})
    const [filter, setFilter] = useState("")
    const [pageChoose, setPageChoose] = useState(1)
    const allOpt = [course, group, lab]


    const callback = () => {
        checkService.postRegister(course.id, group, {...fullUserData}).then(async a => {
            console.log(a.status)
            setMessage(a.data.message)
            setPageChoose(pageChoose + 1)

        }).catch(err => {
            console.log(err.response.data.message)
            console.log(err.response.status)
            setMessage(err.response.data.message)
        })
    }


    const FetchInfo = () => {
        if(pageChoose === 1){
            checkService.getCourses().then(a => setCourses(a))
            setGroups([]);
            setGroup("")
            setLabs([])
            setLab("")
            setMessage("")
            setResult("")
        }
        else if(pageChoose === 2){
            if (groups.length === 0) {
                checkService.getGroups(course.id).
                then(res => {setGroups(res)
                    setCourses([])
                })
            }
            setLabs([])
            setLab("")
            setMessage("")
            setResult("")
        }
        else if(pageChoose === 3){
            if (labs.length === 0) {
                checkService.getLabs(course.id, group).
                then(res => {
                    setLabs(res.data)
                    setGroups([])
                }).catch(err => setLabs([err.response.data.message]))
            }
            setMessage("")
            setResult("")
            setFullUserData({surname: "", name: "", patronymic: "", github: ""})
        }
        else if(pageChoose === 4){
            setLabs([])
            setMessage("")
            setResult("")
        }
        else if(pageChoose === 5){
            checkService.postGrade(course.id, group, lab, fullUserData.github).then(a => {
                setResult(a.data.message)
                console.log(a.status)

            }).catch(err => {
                setResult(err.response.data.message)
                console.log(err.response.status)
                document.getElementsByClassName("result")[0].style.backgroundColor = "red"
            })
        }
    }

    useEffect(() => {
        FetchInfo()
    }, [pageChoose])


    return (
        <>
            <Header text={"Check Lab"}/>

            <div className={"userDiv"}>
                <HaveChoose course={course} group={group} lab={lab} />

                <div className={"chooseParentDiv"}>

                    <InpMes pageChoose={pageChoose} message={message} filter={filter} setFilter={setFilter}/>

                    <div className={"chooseDiv"} style={{ overflowY: pageChoose === 5 ||  pageChoose === 4 ? "hidden" : "scroll" }}>
                        <ChooseArea setCourses={setCourses} getInfo={checkService.getInfoCourse} allOpt={allOpt} strfilt={filter} groups={groups} setGroup={setGroup} courses={courses} setCourse={setCourse} labs={labs} setLab={setLab}/>
                        {pageChoose === 4 && <FormRegister fullUserData={fullUserData} setFullUserData={setFullUserData}/>}
                        {pageChoose === 5 && <div className="resultP">
                            <div className={"result"}>
                                {result}
                            </div>
                        </div>
                        }
                    </div>

                    <div className={"parentArrow"}>
                        <ManageArrow FUD={fullUserData} setFilter={setFilter} allOpt={allOpt} setPageChoose={setPageChoose} pageChoose={pageChoose} callback={callback}/>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Check;