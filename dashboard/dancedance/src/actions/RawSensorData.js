import axios from "axios";
import { GET_ALL_RAW_DATA } from "../reducers/Types";
import { GET_RAW_SENSOR_DATA_API } from "./ApiUrls";

export const getRawSensorData = () => (dispatch, getState) => {
    axios.get(GET_RAW_SENSOR_DATA_API)
        .then((res) => {
            console.log("dispatching")
            dispatch({
                type: GET_ALL_RAW_DATA,
                payload: res.data,
            });
        }).catch((err) => {
            console.log(err);
        });
};