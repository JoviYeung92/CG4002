import axios from "axios";
import { GET_USER_STATISTICS, PUSH_USER_STATISTICS } from "../reducers/Types";
import { GET_USER_STATISTICS_API, PUSH_USER_STATISTICS_API } from "./ApiUrls";

export const getUserStats = (username) => (dispatch, getState) => {
    axios.get(GET_USER_STATISTICS_API+`/?Username=${username}`)
        .then((res) => {
            dispatch({
                type: GET_USER_STATISTICS,
                payload: res.data,
            });
        }).catch((err) => {
            console.log(err);
        });
};

export const pushUserStats = (formData) => (dispatch, getState) => {
    axios.post(PUSH_USER_STATISTICS_API, formData)
        .then((res) => {
            console.log("res.data", res.data)
            dispatch({
                type: PUSH_USER_STATISTICS,
                payload: res.data,
            });
        }).catch((err) => {
            console.log(err);
        });
};