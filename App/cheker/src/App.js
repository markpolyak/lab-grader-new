import {BrowserRouter} from 'react-router-dom'
import './styles/App.css'
import Background from "./Components/Background/Background";
import AppRouter from "./Components/AppRouter/AppRouter";
function App() {

    return (
    <div className="App">
        <div className={"context"}>
            <BrowserRouter>
                <AppRouter/>
            </BrowserRouter>
        </div>

        <Background/>
    </div>
    );
}


export default App;
