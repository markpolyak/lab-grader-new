const express = require('express'); //Строка 1
const checkRoutes = require('./router/check.routes')
const app = express(); //Строка 2
const port =  5000; //Строка 3

const cors = require('cors')
const corsOptions ={
    origin:'*',
    credentials:true,            //access-control-allow-credentials:true
    optionSuccessStatus:200,
}

app.use(cors(corsOptions))
app.use(express.json())
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    next();
});

app.use('/', checkRoutes)

app.listen(port, () => console.log(`Listening on port ${port}`)); //Строка 6


