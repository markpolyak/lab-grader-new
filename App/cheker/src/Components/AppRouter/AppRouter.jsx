import React from 'react';
import {Navigate, Route, Routes} from "react-router-dom";
import {publicRoutes} from "../../router/router";

const AppRouter = () => {
    return (
        <Routes>
            {publicRoutes.map((p) =>
                <Route key={p.path} path={p.path} element={<p.element/>}/>
            )}
            <Route path={"*"} element={<Navigate to={"/check"} replace/>}/>
        </Routes>
    );
};

export default AppRouter;