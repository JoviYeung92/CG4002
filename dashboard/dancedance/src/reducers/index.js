import { combineReducers } from "redux";
import RawSensorData from "./RawSensorData";
import Socket from "./Socket";
import Auth from "./Auth";
import Statistics from "./Statistics"
import DetailedProgress from "./DetailedProgress";

export default combineReducers ({
    RawSensorData,
    Socket,
    Auth,
    Statistics,
    DetailedProgress,
})