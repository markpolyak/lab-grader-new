const express = require('express');
const router = express.Router();

router.get('/courses', (req, res) => { //Строка 9

    res.send([{id: "1",
        name: "История",
        semester: "1"},
        {id: "2",
            name: "Литература",
            semester: "3"},
        {id: "3",
            name: "Информатика",
            semester: "2"},
        {id: "4",
            name: "Структуры и алгоритмы обработки данных",
            semester: "4"},
        {id: "5",
            name: "Веб-технологии",
            semester: "5"},
        {id: "6",
            name: "Бизнес экономика",
            semester: "6"},
        {id: "7",
            name: "Информатика",
            semester: "7"},
        {id: "8",
            name: "Английский язык",
            semester: "5"},
        {id: "9",
            name: "Информатика",
            semester: "4"},
        {id: "10",
            name: "САОД",
            semester: "2"},
        {id: "11",
            name: "Математика",
            semester: "6"}]); //Строка 10
});


router.get('/courses/:course_id/groups', (req, res) => {
    const courseId = req.params.course_id; // Получаем course_id из параметров
    console.log(`Запрошены группы для курса с ID: ${courseId}`);
    if(courseId<5){
        res.send(["4130", "4131", "4132", "4133", "4134", "4135", "4136"])
    }
    else {
        res.send(["4030", "4031", "4032", "4033", "4034", "4035", "4036"])
    }
});

router.get('/courses/:course_id/groups/:group_id/labs', (req, res) => {
    res.send(["0", "1", "2", "3", "4", "5", "6", "7"])
})

router.post('/courses/:course_id/groups/:group_id/register', (req, res) => {
    const {name, surname, patronymic, github} = req.body;
    if(github==="200r" || github==="200w"){
        res.status(200)
        res.send({message: "Аккаунт GitHub успешно задан"})
    }
    else if(github==="202r" || github==="202w"){
        res.status(202)
        res.send({message: "Этот аккаунт GitHub уже был указан ранее для этого же студента. Для изменения аккаунта обратитесь к преподавателю"})
    }
    else{
        res.status(405)
        res.send({message: "Пользователь GitHub не найден"})
    }
})

router.post("/courses/:course_id/groups/:group_id/labs/:lab_id/grade", (req, res) => {
    const {github} = req.body;
    if(github[github.length - 1] === "r"){
        res.status(200)
        res.send({message: "Проверка пройдена успешно"})
    }
    if(github[github.length - 1] === "w"){
        res.status(400)
        res.send({message: "Пройдены не все обязательные тесты"})
    }
})

module.exports = router