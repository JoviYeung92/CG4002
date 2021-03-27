import { GET_SOCKET } from "./Types"

const initialState = {
    socket: null
}

export default (state = initialState, action) => {
    switch (action.type) {
        case GET_SOCKET:
            return {
                ...state,
                socket: action.payload
            }
        default:
            return state;
    }
}