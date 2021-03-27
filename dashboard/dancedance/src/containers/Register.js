import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Redirect, useHistory } from 'react-router-dom';
import { register } from '../actions/Auth';
import { DASHBOARD_ROUTE, LOGIN_ROUTE } from '../routes';

export const Register = () => {
    const [state, setState] = useState({
        username: "",
        password: "",
        passwordTwice: ""
    });
    const [redirect, setRedirect] = useState(false);
    const [registerSuccess, setRegisterSuccess] = useState(false)
    const dispatch = useDispatch();
    const onSubmitHandler = (e) => {
        e.preventDefault();
        if (state.password !== state.passwordTwice) {
            alert("Password doesn't match");
        } else if (state.username === "" || state.password === "" || state.passwordTwice === "") {
            alert("Please fill up the form");
        } else {
            dispatch(register(state.username, state.password));
        }
        setRegisterSuccess(true);
    }

    const onChangeHandler = (e) => {
        setState({
            ...state,
            [e.target.name]: e.target.value,
        });
    };
    const history = useHistory();
    const back = () => {
        setRedirect(true);
    }

    if (redirect) {
        return <Redirect to={LOGIN_ROUTE} />
    } else if (registerSuccess) {
        return <Redirect to={DASHBOARD_ROUTE} />
    } else {
        return (
            <div>
                <div className="col-md-6 m-auto" style={{ width: "150%" }}>
                    <div className="card card-body mt-5">
                        <h3 className="text-center">We are pleased to have you on board, aspiring pro dancer!</h3>
                        <form onSubmit={onSubmitHandler}>
                            <div className="form-group">
                                <label>Username</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    name="username"
                                    onChange={onChangeHandler}
                                    value={state.username}
                                />
                            </div>
                            <div className="form-group">
                                <label>Password</label>
                                <input
                                    type="password"
                                    className="form-control"
                                    name="password"
                                    onChange={onChangeHandler}
                                    value={state.password}
                                />
                            </div>
                            <div className="form-group">
                                <label>Re-type password</label>
                                <input
                                    type="password"
                                    className="form-control"
                                    name="passwordTwice"
                                    onChange={onChangeHandler}
                                    value={state.passwordTwice}
                                />
                            </div>
                            <div className="form-group">
                                <button type="submit" className="btn btn-primary">
                                    Register
                </button>

                                <button type="submit" className="btn btn-primary" style={{ marginLeft: "20px" }} onClick={back}>
                                    Back
   </button>
                            </div>
                        </form>
                    </div>
                </div>
                <div>
                    <span style={{ fontSize: "13px", paddingTop: "20px" }}>
                    </span>
                </div>
            </div>
        )
    }
}