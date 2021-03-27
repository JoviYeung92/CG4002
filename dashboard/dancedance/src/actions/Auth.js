import axios from "axios";
import { USER_LOADED, USER_LOADING, REGISTER_FAILED, REGISTER_SUCCESS, LOGIN_FAILED, LOGIN_SUCCESS, LOGOUT_SUCCESS, AUTH_ERROR } from "../reducers/Types"
import { LOGIN_API, REGISTER_API } from "./ApiUrls";

export const loadUser = () => (dispatch, getState) => {
    const username = localStorage.getItem("username");
    if (username) {
        dispatch({
            type: USER_LOADED,
            payload: username
        })
    }
  };

export const login = (username, password) => (dispatch, getState) => {
    const config = {
        headers: {
            "Content-Type": "application/json",
        }
    }
    const body = JSON.stringify({ Username: username, Password: password });
    console.log(body);
    axios.post(LOGIN_API, body, config)
        .then((res) => {
            res.data.length > 0 ? dispatch({ type: LOGIN_SUCCESS, payload: username }) : dispatch({ type: LOGIN_FAILED });
        }).catch(err => {
            console.log(err);
        })
}

export const register = (username, password) => (dispatch, getState) => {
    const config = {
        headers: {
            "Content-Type": "application/json",
        }
    }
    const body = JSON.stringify({ Username: username, Password: password });
    console.log(body);
    axios.post(REGISTER_API, body, config)
        .then((res) => {
            dispatch({
                type: REGISTER_SUCCESS,
                payload: username
            })
        }).catch(err => {
            console.log(err);
            dispatch({
                type: REGISTER_FAILED
            })
            if (err.response.status === 402) {
                alert("Username is taken");
            }
        })
}

export const logout = () => (dispatch, getState) => {
    dispatch({
        type: LOGOUT_SUCCESS
    })
};