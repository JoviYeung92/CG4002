import React, { useState } from "react";
import { useSelector, useDispatch, shallowEqual } from "react-redux";
import { Redirect, useHistory } from "react-router-dom";
import { DASHBOARD_ROUTE, REGISTER_ROUTE } from "../routes";
import { login } from "../actions/Auth";
import { Container, Row, Col } from "react-bootstrap";
import starry from '../assets/img/starry.png';

export const Login = () => {
    const [state, setState] = useState({
        username: "",
        password: "",
    });
    
    // shallowEqual reduce re-renders whenever redux state refreshes
    const isAuthenticated = useSelector(state => state.Auth.isAuthenticated, shallowEqual); 
    const dispatch = useDispatch();
    const onSubmitHandler = (e) => {
        e.preventDefault();
        dispatch(login(state.username, state.password));
    }

    const onChangeHandler = (e) => {
        setState({
          ...state,
          [e.target.name]: e.target.value,
        });
      };

    if (isAuthenticated) {
        return <Redirect to={DASHBOARD_ROUTE} />;
    } else {
        return (
            <Container fluid>
            <Row style={{height: '100vh'}}>
                <Col style={{backgroundImage: `url(${starry})`}}>
                    <div style={{marginTop: '60px'}}>
                        <p style={{color: 'white', fontSize:'30px'}}>By dancers,</p>
                        <p style={{color: 'white', fontSize:'30px'}}>For dancers</p>
                        <p style={{color: 'white', fontSize:'30px', marginTop: '50px'}}>We have surveyed several passionate dancers and came up with this platform to help you in your journey as an aspiring world-class dancer.</p>
                    </div>
                </Col>
                <Col md={4}>
                        <h1 className="text-center">3, 2, 1, Dance!</h1>
                        <p className="text-center">Welcome, please enter your account information</p>
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
                                <button type="submit" className="btn btn-primary" style={{marginRight: '20px'}}>
                                    Login
                                </button>
                                <button className="btn btn-info">
                                <a href={'#' + REGISTER_ROUTE}>Register an account</a>
                                </button>
                            </div>
                        </form>
                </Col>
            </Row>
            </Container>
        )
    }

}
