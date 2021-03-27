import { GET_ALL_RAW_DATA } from "./Types"

const initialState = {
    sensorData: [],
}

export default (state = initialState, action) => {
    switch (action.type) {
        case GET_ALL_RAW_DATA:
            return {
                ...state,
                sensorData: action.payload
            }
        default:
            return state;
    }
}