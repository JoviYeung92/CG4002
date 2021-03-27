import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { logout } from "../actions/Auth";

export const Navbar = () => {
    const isAuthenticated = useSelector(state => state.Auth.isAuthenticated);
    const dispatch = useDispatch();
    const onClick = () => {
        dispatch(logout());
    }
    return (
        isAuthenticated ? 
        <div>
            <nav className="navbar navbar-expand-lg navbar-light bg-light">
                <a className="navbar-brand" href="#/dashboard">Homepage</a>
                <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <a className="nav-link" href="#/detailed_progress">Detailed progress</a>
                        </li>
                    </ul>
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <a className="nav-link" href="#/practice_mode">Practice mode</a>
                        </li>
                    </ul>
                    <ul className="navbar-nav mr-auto">
                        <li className="nav-item">
                            <a className="nav-link" href="#/evaluation_mode">Evaluation mode</a>
                        </li>
                    </ul>
                    <button className="btn btn-outline-success my-2 my-sm-0" onClick={onClick}>Log out</button>
                </div>
            </nav>
        </div> : null
    );
};

export default Navbar;
