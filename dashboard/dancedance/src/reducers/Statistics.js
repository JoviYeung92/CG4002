import { GET_USER_STATISTICS, PUSH_USER_STATISTICS } from "./Types"

const initialState = {
    userStatistics: null,
}

export default (state = initialState, action) => {
    switch (action.type) {
        case GET_USER_STATISTICS:
            return {
                ...state,
                userStatistics: action.payload
            }
        case PUSH_USER_STATISTICS:
            return {
                ...state,
            }
        default:
            return state;
    }
}